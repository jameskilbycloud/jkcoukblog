/*
 * vmc_analyzer.js — client-side port of vmc_rvtools_analyzer.py
 *
 * Runs the exact same RVTools → VMC-on-AWS checks in the browser, so the
 * Assess tab can analyse a raw .xlsx with no local Python server. Parsing is
 * done by SheetJS (global `XLSX`); this file only implements the rules and the
 * report assembly, mirroring build_report() so the output JSON is identical in
 * shape (schema_version 8) to what the CLI / helper server produce.
 *
 * KEEP IN SYNC with vmc_rvtools_analyzer.py. tools/check_analyzer_parity.py
 * builds a synthetic workbook, runs both, and diffs the reports.
 *
 * Works in the browser (sets window.VMCAnalyzer) and in Node (module.exports),
 * the latter only so the parity check can exercise it.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.VMCAnalyzer = api;
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // ── VMC on AWS limits & constraints (mirror of the Python constants) ──
  const VMC_MAX_VCPU_PER_VM = 128;
  const VMC_MAX_VRAM_MB = 6131712; // ~6 TB
  const VMC_MAX_VMDK_TB = 62;
  const VMC_SUPPORTED_OS = [
    'windows', 'red hat', 'rhel', 'centos', 'ubuntu', 'debian',
    'suse', 'sles', 'oracle linux', 'amazon linux', 'fedora',
    'photon', 'coreos', 'freebsd', 'solaris',
  ];
  const VMC_MIN_HW_VERSION = 4;
  const VMC_HCX_VMOTION_MIN_HW_VERSION = 9;
  const VMC_DEPRECATED_GUEST_IDS = [
    'winnetstandard', 'winnetstandardguest', 'win31', 'win95', 'win98',
    'winme', 'winnt', 'dos', 'os2', 'netware',
  ];
  const VMC_MAX_NICS = 10;
  const VMC_MAX_DISKS = 60;
  const VMC_MAX_SNAPSHOTS_WARN = 3;
  const RAW_DISK_NOTE = 'RDMs (Raw Device Mappings) are NOT supported on VMC on AWS.';
  const ISO_MOUNTED_NOTE = 'Mounted ISOs should be unmounted before migration.';
  const FLOPPY_NOTE = 'Floppy device connected — blocks HCX vMotion specifically (Bulk/Cold Migration are unaffected); remove it before migration.';

  const REMEDIATION = {
    'vcpu-max': 'Reduce the vCPU count, or keep this VM on-prem. No VMC host type '
      + 'presents more than 128 vCPUs to a single VM.',
    'vram-max': 'Reduce the configured memory, or split the workload across VMs. '
      + 'Check the guest actually uses what is assigned before migrating.',
    'hw-version': 'VM hardware version is below vmx-4 — no current ESXi release (VMC\'s '
      + 'included) will power it on. Upgrade to at least vmx-4 while still '
      + 'on-prem; snapshot first, the upgrade requires a power cycle.',
    'hw-version-hcx-migration': 'Runs fine on VMC once there, but below vmx-9 means HCX '
      + 'vMotion/Replication Assisted vMotion/Cold Migration can\'t move it — use '
      + 'HCX OS Assisted Migration instead, or upgrade hardware version on-prem '
      + 'first (snapshot first, requires a power cycle).',
    'guest-os-deprecated': 'Unsupported guest OS. Replatform the application onto a '
      + 'supported OS, or leave the VM on-prem behind a firewall.',
    'guest-os-unverified': 'Cross-check this guest OS against the VMware Compatibility '
      + 'Guide. RVTools often reports \'Other\' when Tools is stale.',
    'tools-not-running': 'Install or start VMware Tools. HCX vMotion and Replication-'
      + 'Assisted vMotion both need it for guest quiescing and network '
      + 'reconfiguration; Bulk/Cold Migration are more tolerant but Tools '
      + 'is still recommended.',
    'hcx-vmotion-poweroff': 'No action needed unless a live migration is specifically '
      + 'wanted for this VM — schedule it under Bulk Migration or '
      + 'Cold Migration instead, or power it on first if HCX vMotion '
      + 'is required.',
    'tools-outdated': 'Upgrade VMware Tools to the version matching the target vSphere '
      + 'release. Schedule it before the wave — most upgrades need a reboot.',
    'fault-tolerance': 'Disable Fault Tolerance before migration. Replace it with '
      + 'vSphere HA plus an application-level clustering option.',
    'vm-encrypted': 'Decrypt the VM before an HCX vMotion, then re-encrypt on arrival '
      + 'using a VMC-side KMS. Bulk migration has the same restriction.',
    'vmdk-max': 'Split the disk, or move the data to a native AWS service such as EBS, '
      + 'FSx, or S3. The 62 TB VMDK ceiling is a hard limit.',
    'rdm': 'Convert the RDM to a VMDK with Storage vMotion before migration, or '
      + 're-present the LUN\'s data from a native AWS service.',
    'disk-count': 'Consolidate disks, or split the VM. Migrate with fewer than 60 disks '
      + 'attached and reattach the remainder afterwards.',
    'nic-legacy': 'Replace the E1000/E1000E adapter with VMXNET3. This changes the guest '
      + 'NIC identity, so re-apply static IP settings after the swap.',
    'portgroup-vlan': 'Map this port group to an NSX segment and confirm whether the '
      + 'network is L2-stretched by HCX or re-IP\'d at cutover.',
    'nic-count': 'Reduce to 10 or fewer NICs. Consider trunking or NSX segments instead '
      + 'of one NIC per VLAN.',
    'snapshot-large': 'Consolidate the snapshot before migration. Large delta files '
      + 'extend transfer time and raise the chance of a failed switchover.',
    'snapshot-count': 'Consolidate the snapshot chain. HCX migrates the base disk plus '
      + 'deltas, so every snapshot adds transfer time and risk.',
    'iso-mounted': 'Disconnect the CD/DVD device and clear the ISO path before an HCX '
      + 'vMotion — a device connected to a host/client device blocks it '
      + 'outright, and a datastore ISO that doesn\'t exist in VMC will too. '
      + 'Bulk/Cold Migration tolerate it, but disconnecting is still good practice.',
    'floppy-attached': 'Remove the floppy device — it\'s a legacy artefact of the VM '
      + 'template with no purpose in VMC, and blocks HCX vMotion '
      + 'specifically (Bulk/Cold Migration are unaffected).',
  };

  const ALL_TABS = ['vInfo', 'vMemory', 'vCPU', 'vDisk', 'vNetwork', 'vSnapshot', 'vCD', 'vFloppy'];
  const OPTIONAL_TABS = new Set(['vFloppy']);

  // ── helpers (mirror finding/to_number/str semantics) ──

  function finding(vm, severity, category, rule, detail) {
    return {
      vm: vm,
      severity: severity,
      category: category,
      rule: rule,
      detail: detail,
      remediation: REMEDIATION[rule] || '',
    };
  }

  // Python round(): round-half-to-even (banker's rounding).
  function pyRound(value, ndigits) {
    if (ndigits === undefined) ndigits = 0;
    if (!isFinite(value)) return value;
    const m = Math.pow(10, ndigits);
    const x = value * m;
    const floor = Math.floor(x);
    const diff = x - floor;
    const eps = 1e-9;
    let r;
    if (Math.abs(diff - 0.5) < eps) {
      r = (floor % 2 === 0) ? floor : floor + 1;
    } else {
      r = Math.round(x);
    }
    // avoid -0 and trim float noise to ndigits
    return Number((r / m).toFixed(Math.max(0, ndigits)));
  }

  // Coerce a cell to a number, tolerating blanks, NaN and text. Mirrors
  // to_number(): str(value).replace(',','').strip() -> float, else default.
  function toNumber(value, def) {
    if (def === undefined) def = 0.0;
    if (typeof value === 'number') return isNaN(value) ? def : value;
    if (value === null || value === undefined) return def;
    let s = String(value).replace(/,/g, '').trim();
    if (s === '') return def; // Python float('') raises -> default
    let n = Number(s);
    return isNaN(n) ? def : n;
  }

  // Mirror Python str(cell). A present-but-empty cell is represented as NaN
  // (see sheetToDf), and Python's str(NaN) is 'nan'.
  function toStr(value) {
    if (typeof value === 'number' && isNaN(value)) return 'nan';
    if (value === null || value === undefined) return '';
    return String(value);
  }

  // Mirror the nested `row.get(a, row.get(b, default))` chain: return the
  // value of the first column key that EXISTS (even if its cell is empty),
  // else the default. Key presence — not truthiness — is what matters, same
  // as pandas Series.get.
  function pick(row, keys, def) {
    for (let i = 0; i < keys.length; i++) {
      if (Object.prototype.hasOwnProperty.call(row, keys[i])) return row[keys[i]];
    }
    return def;
  }

  // ── DataFrame-equivalent from a SheetJS worksheet ──
  // Produces { columns: [normalised headers], rows: [{header: value|NaN}] }.
  // Column names are lowercased+trimmed (normalise_cols). Empty cells become
  // NaN so toStr/toNumber reproduce pandas' NaN handling.
  function sheetToDf(XLSX, ws) {
    const aoa = XLSX.utils.sheet_to_json(ws, { header: 1, raw: true, blankrows: false });
    if (!aoa.length) return { columns: [], rows: [] };
    const headers = (aoa[0] || []).map(function (h) {
      return String(h === null || h === undefined ? '' : h).trim().toLowerCase();
    });
    const rows = [];
    for (let i = 1; i < aoa.length; i++) {
      const arr = aoa[i] || [];
      const obj = {};
      for (let c = 0; c < headers.length; c++) {
        const key = headers[c];
        if (!key) continue;
        let val = arr[c];
        obj[key] = (val === null || val === undefined || val === '') ? NaN : val;
      }
      rows.push(obj);
    }
    return { columns: headers, rows: rows };
  }

  function colsHas(columns, name) { return columns.indexOf(name) !== -1; }

  function isNutanixCvm(vmName) {
    const name = String(vmName === null || vmName === undefined ? '' : vmName).trim().toLowerCase();
    return name.indexOf('ntnx-') === 0 && name.lastIndexOf('-cvm') === name.length - 4 && name.length >= 4;
  }

  // ── analyse_vinfo ──
  function analyseVinfo(df) {
    const findings = [];
    const summary = { total_vms: df.rows.length, powered_on: 0, powered_off: 0, suspended: 0 };
    const excludedInfra = [];

    const totals = { vcpu: 0, vram_gib: 0, provisioned_gib: 0, in_use_gib: 0 };
    const running = { vcpu: 0, vram_gib: 0, provisioned_gib: 0, in_use_gib: 0 };
    const vms = [];

    for (const row of df.rows) {
      const vm = toStr(pick(row, ['vm', 'name'], 'Unknown'));

      if (isNutanixCvm(vm)) { excludedInfra.push(vm); continue; }

      const power = toStr(pick(row, ['powerstate', 'power state'], '')).toLowerCase();
      const isOn = power.indexOf('on') !== -1;
      let powerState;
      if (isOn) { summary.powered_on += 1; powerState = 'on'; }
      else if (power.indexOf('off') !== -1) { summary.powered_off += 1; powerState = 'off'; }
      else { summary.suspended += 1; powerState = 'suspended'; }

      if (!isOn) {
        findings.push(finding(
          vm, 'info', 'HCX', 'hcx-vmotion-poweroff',
          'VM is ' + powerState + ' — HCX vMotion (live migration) is not available for it; '
          + 'use Bulk Migration or Cold Migration instead'));
      }

      const cpus = toNumber(pick(row, ['cpus', 'num cpu'], 0));
      const memMb = toNumber(pick(row, ['memory', 'memory mb'], 0));
      const provMb = toNumber(pick(row, ['provisioned mib', 'provisioned mb', 'provisioned'], 0));
      const usedMb = toNumber(pick(row, ['in use mib', 'in use mb', 'in use'], 0));

      const rowTotals = {
        vcpu: cpus,
        vram_gib: memMb / 1024,
        provisioned_gib: provMb / 1024,
        in_use_gib: usedMb / 1024,
      };
      for (const key in rowTotals) {
        totals[key] += rowTotals[key];
        if (isOn) running[key] += rowTotals[key];
      }

      let vcCluster = toStr(pick(row, ['cluster'], '')).trim();
      if (['', 'nan', 'none'].indexOf(vcCluster.toLowerCase()) !== -1) vcCluster = '';

      vms.push({
        vm: vm,
        power_state: powerState,
        vcpu: pyRound(cpus, 1),
        vram_gib: pyRound(memMb / 1024, 2),
        provisioned_gib: pyRound(provMb / 1024, 2),
        in_use_gib: pyRound(usedMb / 1024, 2),
        vc_cluster: vcCluster,
      });

      // ── Checks ──
      if (cpus > VMC_MAX_VCPU_PER_VM) {
        findings.push(finding(
          vm, 'blocker', 'Compute', 'vcpu-max',
          'VM has ' + Math.trunc(cpus) + ' vCPUs — exceeds VMC max of ' + VMC_MAX_VCPU_PER_VM));
      }
      if (memMb > VMC_MAX_VRAM_MB) {
        findings.push(finding(
          vm, 'blocker', 'Compute', 'vram-max',
          'VM has ' + Math.trunc(memMb) + ' MB RAM — exceeds VMC max of ' + VMC_MAX_VRAM_MB + ' MB'));
      }

      const hwRaw = pick(row, ['hardware version', 'hw version'], '');
      let hwVer = 0;
      const hwParsed = parseInt(toStr(hwRaw).replace('vmx-', ''), 10);
      if (!isNaN(hwParsed)) hwVer = hwParsed;
      if (hwVer > 0 && hwVer < VMC_MIN_HW_VERSION) {
        findings.push(finding(
          vm, 'blocker', 'Compatibility', 'hw-version',
          'Hardware version vmx-' + hwVer + ' — below vmx-' + VMC_MIN_HW_VERSION + ', the floor '
          + 'below which no current ESXi release (VMC\'s included) will power the VM on'));
      } else if (hwVer >= VMC_MIN_HW_VERSION && hwVer < VMC_HCX_VMOTION_MIN_HW_VERSION) {
        findings.push(finding(
          vm, 'info', 'Compatibility', 'hw-version-hcx-migration',
          'Hardware version vmx-' + hwVer + ' — runs fine on VMC, but below what HCX '
          + 'vMotion/Replication Assisted vMotion/Cold Migration need '
          + '(vmx-' + VMC_HCX_VMOTION_MIN_HW_VERSION + '+); use HCX OS Assisted Migration instead '
          + '(no hardware-version requirement), or upgrade the VM\'s hardware version '
          + 'on-prem first'));
      }

      const guest = toStr(pick(row, ['os according to the vmware tools', 'os', 'guest os'], '')).toLowerCase();
      const configGuest = toStr(pick(row, ['os according to the configuration file', 'config os'], '')).toLowerCase();
      const combinedOs = guest + ' ' + configGuest;

      if (VMC_DEPRECATED_GUEST_IDS.some(function (dep) { return combinedOs.indexOf(dep) !== -1; })) {
        findings.push(finding(
          vm, 'blocker', 'OS', 'guest-os-deprecated',
          'Deprecated/unsupported guest OS detected: ' + (guest || configGuest)));
      } else if (!VMC_SUPPORTED_OS.some(function (s) { return combinedOs.indexOf(s) !== -1; }) && combinedOs.trim()) {
        findings.push(finding(
          vm, 'warning', 'OS', 'guest-os-unverified',
          'OS may not be supported — verify: ' + (guest || configGuest)));
      }

      let tools = toStr(pick(row, ['tools status', 'vmware tools status'], '')).toLowerCase().replace(/ /g, '');
      if (isOn && tools && tools !== 'nan' && tools !== 'none') {
        if (tools.indexOf('notinstalled') !== -1 || tools.indexOf('notrunning') !== -1) {
          findings.push(finding(
            vm, 'warning', 'Tools', 'tools-not-running',
            'VMware Tools not running (status: ' + tools + ') — blocks HCX vMotion and '
            + 'Replication-Assisted vMotion (both need Tools for guest quiescing); '
            + 'install/start before migration'));
        } else if (tools.indexOf('old') !== -1 || tools.indexOf('outofdate') !== -1 || tools.indexOf('needupgrade') !== -1) {
          findings.push(finding(
            vm, 'info', 'Tools', 'tools-outdated',
            'VMware Tools out of date (status: ' + tools + ') — upgrade before migration'));
        }
      }

      const ft = toStr(pick(row, ['fault tolerance state', 'ft state'], '')).toLowerCase();
      if (ft && ['', 'notconfigured', 'not configured', 'nan', 'none'].indexOf(ft) === -1) {
        findings.push(finding(
          vm, 'blocker', 'Feature', 'fault-tolerance',
          'Fault Tolerance enabled (' + ft + ') — not supported on VMC on AWS'));
      }

      const encrypted = toStr(pick(row, ['encrypted'], '')).toLowerCase();
      if (['true', 'yes', '1'].indexOf(encrypted) !== -1) {
        findings.push(finding(
          vm, 'warning', 'Security', 'vm-encrypted',
          'VM is encrypted — must decrypt before migration via HCX'));
      }
    }

    // total_vms is the migratable estate, net of excluded infrastructure.
    summary.total_vms = df.rows.length - excludedInfra.length;
    summary.excluded_infra = excludedInfra.length;

    const capacity = {
      vms_counted: vms.length,
      excluded_infra: excludedInfra.length,
      excluded_infra_vms: excludedInfra,
      total: roundObj(totals, 1),
      powered_on: roundObj(running, 1),
      vms: vms,
    };
    return { findings: findings, summary: summary, capacity: capacity };
  }

  function roundObj(obj, ndigits) {
    const out = {};
    for (const k in obj) out[k] = pyRound(obj[k], ndigits);
    return out;
  }

  // ── vMemory / vCPU column resolvers + readers ──
  const VMEMORY_CONSUMED_CANDIDATES = [
    'consumed mib', 'consumed mb', 'consumed',
    'consumed (mib)', 'consumed (mb)', 'consumed(mib)', 'consumed(mb)',
    'consumed memory', 'host mem consumed', 'consumed host memory',
  ];
  function resolveVmemoryConsumedColumn(columns) {
    for (const c of VMEMORY_CONSUMED_CANDIDATES) if (colsHas(columns, c)) return c;
    for (const col of columns) {
      if (col.indexOf('consumed') === 0 && col.indexOf('overhead') === -1 && col.indexOf('%') === -1) return col;
    }
    return null;
  }

  const VCPU_OVERALL_CANDIDATES = [
    'overall', 'overall cpu usage', 'overall cpu usage (mhz)',
    'cpu usage (mhz)', 'cpu usage', 'usage (mhz)',
  ];
  const VCPU_MAX_CANDIDATES = ['max', 'max mhz', 'max (mhz)', 'max cpu usage (mhz)'];
  function resolveVcpuColumn(columns, candidates, prefix, exclude) {
    exclude = exclude || [];
    for (const c of candidates) if (colsHas(columns, c)) return c;
    for (const col of columns) {
      if (col.indexOf(prefix) === 0 && !exclude.some(function (bad) { return col.indexOf(bad) !== -1; })) return col;
    }
    return null;
  }
  function resolveVcpuOverallColumn(columns) {
    return resolveVcpuColumn(columns, VCPU_OVERALL_CANDIDATES, 'overall', ['readiness', '%']);
  }
  function resolveVcpuMaxColumn(columns) {
    return resolveVcpuColumn(columns, VCPU_MAX_CANDIDATES, 'max', ['%']);
  }

  function readVcpuUsage(df) {
    const overallCol = resolveVcpuOverallColumn(df.columns);
    const maxCol = resolveVcpuMaxColumn(df.columns);
    const usage = {};
    for (const row of df.rows) {
      const vm = toStr(pick(row, ['vm', 'name'], 'Unknown'));
      const cpus = toNumber(pick(row, ['cpus', 'num cpu'], 0));
      if (!overallCol || !maxCol) { usage[vm] = 0.0; continue; }
      const overall = toNumber(pick(row, [overallCol], 0));
      const vmax = toNumber(pick(row, [maxCol], 0));
      usage[vm] = (vmax > 0) ? (cpus * overall / vmax) : 0.0;
    }
    return usage;
  }

  function readVmemoryConsumed(df) {
    const col = resolveVmemoryConsumedColumn(df.columns);
    const consumed = {};
    for (const row of df.rows) {
      const vm = toStr(pick(row, ['vm', 'name'], 'Unknown'));
      consumed[vm] = col ? toNumber(pick(row, [col], 0)) : 0.0;
    }
    return consumed;
  }

  // ── vDisk / vNetwork / vSnapshot / vCD / vFloppy ──
  function analyseVdisk(df) {
    const findings = [];
    const vmDiskCounts = {};
    for (const row of df.rows) {
      const vm = toStr(pick(row, ['vm', 'name'], 'Unknown'));
      vmDiskCounts[vm] = (vmDiskCounts[vm] || 0) + 1;

      const capTb = toNumber(pick(row, ['capacity mib', 'capacity mb', 'capacity'], 0)) / 1048576;
      if (capTb > VMC_MAX_VMDK_TB) {
        findings.push(finding(
          vm, 'blocker', 'Storage', 'vmdk-max',
          'Disk ' + capTb.toFixed(1) + ' TB exceeds VMC max of ' + VMC_MAX_VMDK_TB + ' TB'));
      }

      const raw = toStr(pick(row, ['raw', 'rdm', 'disk type'], '')).toLowerCase();
      if (raw.indexOf('rdm') !== -1 || raw.indexOf('raw') !== -1 || raw === 'true' || raw === 'yes') {
        findings.push(finding(vm, 'blocker', 'Storage', 'rdm', RAW_DISK_NOTE));
      }
    }
    for (const vm in vmDiskCounts) {
      if (vmDiskCounts[vm] > VMC_MAX_DISKS) {
        findings.push(finding(
          vm, 'blocker', 'Storage', 'disk-count',
          'VM has ' + vmDiskCounts[vm] + ' disks — exceeds VMC max of ' + VMC_MAX_DISKS));
      }
    }
    return findings;
  }

  function analyseVnetwork(df) {
    const findings = [];
    const vmNicCounts = {};
    for (const row of df.rows) {
      const vm = toStr(pick(row, ['vm', 'name'], 'Unknown'));
      vmNicCounts[vm] = (vmNicCounts[vm] || 0) + 1;

      const adapter = toStr(pick(row, ['adapter type', 'type'], '')).toLowerCase();
      if (adapter.indexOf('e1000') !== -1) {
        findings.push(finding(
          vm, 'warning', 'Network', 'nic-legacy',
          'Legacy adapter (' + adapter + ') — switch to VMXNET3 for best VMC performance'));
      }

      const pg = toStr(pick(row, ['port group', 'network'], '')).toLowerCase();
      if (pg.indexOf('vlan') !== -1 || pg.indexOf('trunk') !== -1) {
        findings.push(finding(
          vm, 'info', 'Network', 'portgroup-vlan',
          'Uses VLAN/trunk port-group \'' + pg + '\' — verify NSX segment mapping in VMC'));
      }
    }
    for (const vm in vmNicCounts) {
      if (vmNicCounts[vm] > VMC_MAX_NICS) {
        findings.push(finding(
          vm, 'blocker', 'Network', 'nic-count',
          'VM has ' + vmNicCounts[vm] + ' NICs — exceeds VMC max of ' + VMC_MAX_NICS));
      }
    }
    return findings;
  }

  function analyseVsnapshot(df) {
    const findings = [];
    const vmSnapCounts = {};
    for (const row of df.rows) {
      const vm = toStr(pick(row, ['vm', 'name'], 'Unknown'));
      vmSnapCounts[vm] = (vmSnapCounts[vm] || 0) + 1;

      const sizeGb = toNumber(pick(row, ['size mib', 'size mb', 'size'], 0)) / 1024;
      if (sizeGb > 50) {
        findings.push(finding(
          vm, 'warning', 'Snapshot', 'snapshot-large',
          'Large snapshot (' + sizeGb.toFixed(1) + ' GB) — consolidate before migration'));
      }
    }
    for (const vm in vmSnapCounts) {
      if (vmSnapCounts[vm] > VMC_MAX_SNAPSHOTS_WARN) {
        findings.push(finding(
          vm, 'warning', 'Snapshot', 'snapshot-count',
          'VM has ' + vmSnapCounts[vm] + ' snapshots — consolidate before migration for best performance'));
      }
    }
    return findings;
  }

  function analyseVcd(df) {
    const findings = [];
    for (const row of df.rows) {
      const vm = toStr(pick(row, ['vm', 'name'], 'Unknown'));
      const connected = toStr(pick(row, ['connected'], '')).toLowerCase();
      const iso = toStr(pick(row, ['iso', 'iso path'], '')).trim();
      const hasIso = !!iso && ['', 'nan', 'none'].indexOf(iso.toLowerCase()) === -1;
      if (connected === 'true' || connected === 'yes' || hasIso) {
        let detail;
        if (hasIso) {
          detail = ISO_MOUNTED_NOTE + ' (ISO: ' + iso + ')';
        } else {
          detail = ISO_MOUNTED_NOTE + ' Connected with no datastore ISO path — likely a '
            + 'host/client device, which blocks HCX vMotion specifically.';
        }
        findings.push(finding(vm, 'warning', 'Device', 'iso-mounted', detail));
      }
    }
    return findings;
  }

  function analyseVfloppy(df) {
    const findings = [];
    for (const row of df.rows) {
      const vm = toStr(pick(row, ['vm', 'name'], 'Unknown'));
      const connected = toStr(pick(row, ['connected'], '')).toLowerCase();
      if (connected === 'true' || connected === 'yes') {
        findings.push(finding(vm, 'warning', 'Device', 'floppy-attached', FLOPPY_NOTE));
      }
    }
    return findings;
  }

  // ── sheet lookup (exact, then case-insensitive) ──
  function findSheet(XLSX, workbook, name) {
    if (workbook.Sheets[name]) return workbook.Sheets[name];
    const lower = name.toLowerCase();
    for (const sn of workbook.SheetNames) {
      if (sn.toLowerCase() === lower) return workbook.Sheets[sn];
    }
    return null;
  }

  function safeDf(XLSX, workbook, name) {
    const ws = findSheet(XLSX, workbook, name);
    if (!ws) return null;
    return sheetToDf(XLSX, ws);
  }

  // ── analyse_workbook (one SheetJS workbook) ──
  function analyseWorkbook(XLSX, workbook) {
    const allFindings = [];
    let summary = {};
    let capacity = {};
    const tabsProcessed = [];
    const tabsMissing = [];

    // vInfo
    let df = safeDf(XLSX, workbook, 'vInfo');
    if (df) {
      const r = analyseVinfo(df);
      allFindings.push.apply(allFindings, r.findings);
      summary = r.summary;
      capacity = r.capacity;
      tabsProcessed.push('vInfo');
    } else {
      tabsMissing.push('vInfo');
    }

    // vMemory (consumed memory)
    let consumedByVm = {};
    df = safeDf(XLSX, workbook, 'vMemory');
    if (df) {
      consumedByVm = readVmemoryConsumed(df);
      if (resolveVmemoryConsumedColumn(df.columns) !== null) tabsProcessed.push('vMemory');
      else tabsMissing.push('vMemory');
    } else {
      tabsMissing.push('vMemory');
    }
    if (capacity.vms) {
      let totalConsumed = 0, runningConsumed = 0;
      for (const v of capacity.vms) {
        const consumedGib = pyRound((consumedByVm[v.vm] || 0) / 1024, 2);
        v.consumed_vram_gib = consumedGib;
        totalConsumed += consumedGib;
        if (v.power_state === 'on') runningConsumed += consumedGib;
      }
      capacity.total.consumed_vram_gib = pyRound(totalConsumed, 1);
      capacity.powered_on.consumed_vram_gib = pyRound(runningConsumed, 1);
    }

    // vCPU (actual CPU demand)
    let vcpuUsageByVm = {};
    df = safeDf(XLSX, workbook, 'vCPU');
    if (df) {
      vcpuUsageByVm = readVcpuUsage(df);
      if (resolveVcpuOverallColumn(df.columns) !== null && resolveVcpuMaxColumn(df.columns) !== null) tabsProcessed.push('vCPU');
      else tabsMissing.push('vCPU');
    } else {
      tabsMissing.push('vCPU');
    }
    if (capacity.vms) {
      let totalConsumed = 0, runningConsumed = 0;
      for (const v of capacity.vms) {
        const consumedVcpu = pyRound(vcpuUsageByVm[v.vm] || 0, 2);
        v.consumed_vcpu = consumedVcpu;
        totalConsumed += consumedVcpu;
        if (v.power_state === 'on') runningConsumed += consumedVcpu;
      }
      capacity.total.consumed_vcpu = pyRound(totalConsumed, 1);
      capacity.powered_on.consumed_vcpu = pyRound(runningConsumed, 1);
    }

    // vDisk
    df = safeDf(XLSX, workbook, 'vDisk');
    if (df) { allFindings.push.apply(allFindings, analyseVdisk(df)); tabsProcessed.push('vDisk'); }
    else tabsMissing.push('vDisk');

    // vNetwork
    df = safeDf(XLSX, workbook, 'vNetwork');
    if (df) { allFindings.push.apply(allFindings, analyseVnetwork(df)); tabsProcessed.push('vNetwork'); }
    else tabsMissing.push('vNetwork');

    // vSnapshot (or legacy vSnap)
    let snapDone = false;
    for (const tabName of ['vSnapshot', 'vSnap']) {
      df = safeDf(XLSX, workbook, tabName);
      if (df) { allFindings.push.apply(allFindings, analyseVsnapshot(df)); tabsProcessed.push('vSnapshot'); snapDone = true; break; }
    }
    if (!snapDone) tabsMissing.push('vSnapshot');

    // vCD
    df = safeDf(XLSX, workbook, 'vCD');
    if (df) { allFindings.push.apply(allFindings, analyseVcd(df)); tabsProcessed.push('vCD'); }
    else tabsMissing.push('vCD');

    // vFloppy
    df = safeDf(XLSX, workbook, 'vFloppy');
    if (df) { allFindings.push.apply(allFindings, analyseVfloppy(df)); tabsProcessed.push('vFloppy'); }
    else tabsMissing.push('vFloppy');

    return { tabsProcessed: tabsProcessed, tabsMissing: tabsMissing, summary: summary, capacity: capacity, findings: allFindings };
  }

  function sevCounts(findings) {
    const counts = { blocker: 0, warning: 0, info: 0 };
    for (const f of findings) counts[f.severity || 'info'] += 1;
    return counts;
  }
  function affectedVms(findings) {
    const s = new Set();
    for (const f of findings) s.add(f.vm);
    return Array.from(s).sort();
  }

  // ── build_report — sources: [{name, workbook}] (SheetJS workbooks) ──
  function buildReport(XLSX, sources) {
    const capacityKeys = ['vcpu', 'consumed_vcpu', 'vram_gib', 'consumed_vram_gib', 'provisioned_gib', 'in_use_gib'];
    const combinedSummary = { total_vms: 0, powered_on: 0, powered_off: 0, suspended: 0, excluded_infra: 0 };
    const combinedTotal = {}; capacityKeys.forEach(function (k) { combinedTotal[k] = 0; });
    const combinedRunning = {}; capacityKeys.forEach(function (k) { combinedRunning[k] = 0; });
    let vmsCounted = 0;

    const allFindings = [];
    const allVms = [];
    const excludedInfraVms = [];
    const tabsProcessedUnion = new Set();
    const sourcesOut = {};
    const skippedSources = [];
    const processedNames = [];

    for (const src of sources) {
      const name = src.name;
      let res;
      try {
        res = analyseWorkbook(XLSX, src.workbook);
      } catch (exc) {
        skippedSources.push({ source_file: name, error: String(exc && exc.message ? exc.message : exc) });
        continue;
      }

      for (const f of res.findings) f.source = name;
      allFindings.push.apply(allFindings, res.findings);

      const caps = res.capacity.vms || [];
      for (const v of caps) allVms.push(Object.assign({}, v, { source: name }));

      for (const key in combinedSummary) combinedSummary[key] += (res.summary[key] || 0);
      const capTotal = res.capacity.total || {};
      const capRunning = res.capacity.powered_on || {};
      for (const key of capacityKeys) {
        combinedTotal[key] += (capTotal[key] || 0);
        combinedRunning[key] += (capRunning[key] || 0);
      }
      vmsCounted += (res.capacity.vms_counted || 0);
      for (const cvm of (res.capacity.excluded_infra_vms || [])) excludedInfraVms.push({ vm: cvm, source: name });

      res.tabsProcessed.forEach(function (t) { tabsProcessedUnion.add(t); });
      const tabsMissing = res.tabsMissing.filter(function (t) { return !OPTIONAL_TABS.has(t); });

      sourcesOut[name] = {
        tabs_processed: res.tabsProcessed,
        tabs_missing: tabsMissing,
        summary: res.summary,
        capacity: res.capacity,
        severity_counts: sevCounts(res.findings),
        affected_vm_count: affectedVms(res.findings).length,
        total_findings: res.findings.length,
      };
      processedNames.push(name);
    }

    let sourceFileField;
    if (processedNames.length === 1) sourceFileField = processedNames[0];
    else if (processedNames.length > 1) sourceFileField = processedNames.length + ' sources merged';
    else sourceFileField = null;

    const tabsProcessedTop = ALL_TABS.filter(function (t) { return tabsProcessedUnion.has(t); });
    const tabsMissingTop = ALL_TABS.filter(function (t) { return !tabsProcessedUnion.has(t) && !OPTIONAL_TABS.has(t); });

    return {
      schema_version: 8,
      generated: new Date().toISOString(),
      source_file: sourceFileField,
      source_files: processedNames,
      skipped_sources: skippedSources,
      tabs_processed: tabsProcessedTop,
      tabs_missing: tabsMissingTop,
      summary: combinedSummary,
      capacity: {
        vms_counted: vmsCounted,
        excluded_infra: excludedInfraVms.length,
        excluded_infra_vms: excludedInfraVms,
        total: roundObj(combinedTotal, 1),
        powered_on: roundObj(combinedRunning, 1),
      },
      severity_counts: sevCounts(allFindings),
      affected_vm_count: affectedVms(allFindings).length,
      total_findings: allFindings.length,
      findings: allFindings,
      vms: allVms,
      sources: sourcesOut,
    };
  }

  // Browser convenience: build a report from File/ArrayBuffer inputs.
  // `inputs` = [{name, data}] where data is an ArrayBuffer/Uint8Array.
  function buildReportFromBuffers(XLSX, inputs) {
    const sources = inputs.map(function (inp) {
      const wb = XLSX.read(inp.data, { type: 'array' });
      return { name: inp.name, workbook: wb };
    });
    return buildReport(XLSX, sources);
  }

  return {
    buildReport: buildReport,
    buildReportFromBuffers: buildReportFromBuffers,
    analyseWorkbook: analyseWorkbook,
    sheetToDf: sheetToDf,
    isNutanixCvm: isNutanixCvm,
    toNumber: toNumber,
    pyRound: pyRound,
    SCHEMA_VERSION: 8,
  };
}));
