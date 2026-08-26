---
title: "VMware Cloud on AWS (VMC) – Links & Resources"
description: "Curated VMware Cloud on AWS (VMC) resources: official docs, release notes, HCX, networking, automation, Aria integration and hands-on blogs."
date: 2025-03-18T12:20:48+00:00
modified: 2026-07-23T21:01:31+00:00
author: James Kilby
categories:
  - Patrick Kremer
url: https://jameskilby.co.uk/vmc/
image: https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-1024x526.png
---

# VMware Cloud on AWS (VMC) – Links & Resources  
  
This page is a curated hub of links, documentation and tools for **VMware Cloud on AWS (VMC)** — Broadcom’s managed VMware-as-a-service running on dedicated AWS bare-metal hosts. It covers service status, design and sizing, networking, HCX migration, automation (PowerCLI, Terraform, API), Aria integration, security, performance, workloads (SQL, Oracle) and VMware Live Recovery.

In my role at Broadcom I look after the VMware-on-AWS HyperScaler solutions — VMware Cloud on AWS (VMC) and[ Elastic VMware Service (EVS)](https://jameskilby.co.uk/evs/). The shortcuts below are the public docs I use day-to-day.

## Table of Contents

## Service Status

[Status Page](https://status.broadcom.com/services/vmware-cloud-services)

### VMware Cloud Console

[Cloud Console](https://console.cloud.broadcom.com)

[VMC Console](https://vmc.broadcom.com)

## FAQ

[Overview](https://vmc.broadcom.com/infrastructure/aws/overview)

[FAQ](https://www.vmware.com/docs/vmware-cloud-on-aws-frequently-asked-questions)

[Continuation Statement](https://www.broadcom.com/blog/vmware-cloud-on-aws-here-today-here-tomorrow?utm_source=linkedin&utm_medium=social&utm_campaign=broadcom-blog)

[TCO Whitepaper](https://www.vmware.com/docs/vmw-comparing-vmc-to-traditional-public-cloud)

## Design

[Release Notes](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/vmware-cloud-on-aws-release-notes.html)

[Interop Matrix](https://interopmatrix.broadcom.com/Interoperability?col=648,&row=0)

[Pre Requisites](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud/cloud/vmware-cloud-gateway-administration/installing-and-configuring-vcenter-cloud-gateway/prerequisites-for-vmware-cloud-on-aws.html)

[Getting Started](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/vmware-cloud-on-aws-getting-started.html)

[Sizing](https://vmc.broadcom.com/sizer/home)

[Legacy Sizer](https://vmc.vmware.com/sizer/aws/advanced-sizing/v5)

[Configuration Maximums](https://configmax.broadcom.com/guest?vmwareproduct=VMware%20Cloud%20on%20AWS&release=SDDC%201.24&categories=3-0) ( Current SDDC Version)

[Guest OS Support](https://compatibilityguide.broadcom.com/search?program=software&persona=live&column=osVendors&order=asc)

[Stretched Clusters](https://www.vmware.com/docs/vmware-cloud-on-aws-stretched-clusters)

[Entry Level Clusters](https://www.vmware.com/docs/entry-level-clusters-on-vmware-cloud-on-aws#section)

[FSx for NetApp ONTAP](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/operations-guide/accessing-aws-services/configure-amazon-fsx-as-external-storage.html)

### Compliance

[Compliance Center](https://www.broadcom.com/support/trust-center/compliance?service\[\]=VMware%20Cloud%20on%20AWS)

## Automation (PowerCLI, Terraform, API)

[Developer Center](https://developer.broadcom.com/xapis/vmware-cloud-on-aws-api/VMC%20on%20AWS%201.9/)

[API Usage Reporting ](https://developer.broadcom.com/xapis/vmc-on-aws-general/latest/api/activityanalytic/org_id/hosts/freq/usage-report/get/)

[PowerCLI](https://developer.broadcom.com/powercli/latest/products/vmwarecloudonaws/)

[Terraform ](https://registry.terraform.io/providers/vmware/vmc/latest/docs)

[Import/Export](https://community.broadcom.com/vmware-code/viewdocument/sddc-import-export-for-vmware-cloud?CommunityKey=d743a854-b7b6-437f-9698-4dd8983b11cf&tab=librarydocuments)

## Authentication

[Federating Login](https://www.vmware.com/docs/feature-brief-vcenter-federated-login-for-vmware-cloud-on-aws)

## Operations

[Operations Guide](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/operations-guide.html)

[Build Numbers](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/operations-guide/about-software-defined-data-centers/vsphere-components-and-interfaces/correlating-vmware-cloud-on-aws-with-component-releases.html)

[SLA](https://www.vmware.com/docs/vmw-cloud-aws-service-level-agreement)

[Cluster Conversion](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/operations-guide/managing-sddc-hosts-and-clusters/converting-host-types.html)

[Troubleshooting](https://knowledge.broadcom.com/external/article?legacyId=77167)

[VMware Tools Interoperability](https://interopmatrix.broadcom.com/Interoperability?col=648,9676,17083&row=139)

[Penetration Testing](https://knowledge.broadcom.com/external/article/334958)

[Organisation Hold](https://ftpdocs.broadcom.com/cadocs/0/contentimages/Cloud_Services_Console_on_Broadcom_External_User_Guide_v5.pdf)

## Networking

[Networking and Security Guide](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/vmware-cloud-on-aws-networking-and-security.html)

[SDDC Groups & VMware Transit Connect](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/vmware-cloud-on-aws-networking-and-security/configuring-vmware-cloud-on-aws-networking-using-nsx-t/creating-and-managing-sddc-groups.html)

[NSX Advanced Firewall (vDefend)](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/operations-guide/working-with-sddc-add-on-services/using-the-nsx-advanced-firewall-service.html)

[IPv6 in SDDC Networks](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/vmware-cloud-on-aws-networking-and-security/configuring-vmware-cloud-on-aws-networking-using-nsx-t/about-ipv6.html)

[AWS Direct Connect Integration (AWS)](https://aws.amazon.com/blogs/apn/aws-direct-connect-integration-with-vmware-cloud-on-aws/)

[Third-Party Firewalls via Transit Connect (AWS)](https://aws.amazon.com/blogs/apn/integrating-third-party-firewall-appliances-with-vmware-cloud-on-aws-using-vmware-transit-connect/)

### Microsoft SPLA

[SPLA Overview](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/operations-guide/about-managing-virtual-machines-in-vmware-cloud-on-aws/microsoft-product-licenses-in-vmware-cloud-on-aws.html)

## Aria Integration

### Aria Operations

[How to connect from Aria Operations to VMC](https://techdocs.broadcom.com/us/en/vmware-cis/aria/aria-operations/8-18/vmware-aria-operations-configuration-guide-8-18/connect-to-data-sources/management-pack-for-vmware-cloud-on-aws/configure-vmware-cloud-on-aws-in-vrealize-operations.html)

[VMC Monitoring from Aria ](https://techdocs.broadcom.com/us/en/vmware-cis/aria/aria-operations/8-16/vmware-aria-operations-user-guide-8-16/metric-property-and-alert-definitions/metrics-definitions-in-vrealize-operations-manager/metrics-in-vmware-cloud-on-aws.html)

### Aria Automation

[How to connect from Aria Automation to VMC](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/operations-guide/using-on-premises-vrealize-automation-with-your-cloud-sddc/connect-vrealize-automation-to-your-sdc.html)

### Aria Operations for Networks

[How to connect from Aria Operations for Networks to VMC](https://techdocs.broadcom.com/us/en/vmware-cis/aria/aria-operations-for-networks/6-14/vrealize-network-insight-ug-4-1-and-later-6-14/adding-a-data-source-in-vrealize-network-insight/supported-vmc-accounts/manual-configuration/add-vmc-on-aws-nsx-manager.html)

## Security

[Broadcom security announcements ](https://github.com/vmware/vcf-security-and-compliance-guidelines)

[Privacy](https://www.vmware.com/docs/vmw-datasheet-vmc-on-aws-privacy)

## Performance

[IDS Dashboard](https://community.broadcom.com/applications-networking-security/discussion/new-aria-operations-dashboard-for-idps)

[Performance Best Practices for VMC](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/performance-best-practices-for-vmc.html)

## HCX

[Config Max](https://configmax.broadcom.com/guest?vmwareproduct=VMware%20HCX&release=VMware%20HCX%204.10.0&categories=41-0)

[Release Notes](https://techdocs.broadcom.com/us/en/vmware-cis/hcx/vmware-hcx/4-11.html)

[Upgrading HCX in VMC](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/operations-guide/about-managing-virtual-machines-in-vmware-cloud-on-aws/migrating-virtual-machines/hcx-migration/upgrade-hcx-for-vmware-cloud-on-aws.html)

[HCX Port Diagram](https://hcx.design/wp-content/uploads/2019/12/hcx-network-ports-1.pdf)

## Miscellaneous VMC Articles

[Rvtools Bug](https://repost.aws/articles/ARkRdniPpcS_y1eNz6_W1T4w/rvtools-4-7-1-bug-with-vmware-cloud-on-aws)

## Workloads

### SQL

[Performance Whitepaper](https://www.vmware.com/docs/sql-server-vmc-aws-perf-1)

[Block alignment optimisation](https://blogs.vmware.com/apps/2021/12/enhancing-performance-vmc-on-aws-sql-server-trace-flag-1800.html)

### Oracle

[Oracle licensing on VMC](https://blogs.vmware.com/apps/2018/02/oracle-vmware-cloud-aws-unraveling-myth.html)

[Oracle publications by Sudhir](https://vracdba.com/publications-2/)

[Database Performance on VMC](https://www.vmware.com/docs/oracle-vmc-aws-i4i)

[Oracle DR](https://www.vmware.com/docs/vmw-oracle-bc-dr-vmware-multi-cloud)

## Official Blogs I contributed to

[VMware Cloud on AWS: SDDC Version 1.26 Release](https://blogs.vmware.com/cloud-foundation/2026/01/23/vmware-cloud-on-aws-sddc-version-1-26-release/)

[VMware Cloud on AWS: What’s New (December 2025)](https://blogs.vmware.com/cloud-foundation/2025/12/02/vmware-cloud-on-aws-whats-new-december-2025/)

## My VMware Cloud on AWS Blog Posts

[Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

[Time in a VMC Environment](https://jameskilby.co.uk/2025/12/time-in-a-vmc-environment/)

[An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMC – vSAN ESA](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)

## Useful Knowledge Base Articles

[Cross vC vMotion](https://knowledge.broadcom.com/external/article?legacyId=79446)

## VMware Live Recovery

[VLCR (formerly VCDR – VMware Cloud Disaster Recovery)](https://techdocs.broadcom.com/us/en/vmware-cis/live-recovery/live-cyber-recovery/saas.html)

[VLCR Planner](https://vcdr-planner.esp.vmware.com/)

## Learning

[VMware Cloud on AWS Hands-on Labs (HOL)](https://www.vmware.com/go/try-vmc-aws-hol)

## Useful Blogs

[William Lam](https://williamlam.com/?s=vmc)

[Michael Armstrong](https://www.m80arm.co.uk/)

[Dan Firth](https://www.penguinpunk.net/blog/)

[Chris Dooks](https://chrisdooks.com/)

[Patrick Kremer](https://www.patrickkremer.com/category/vmware/vmconaws/)

[Nikolay Kulikov](https://nkulikov.com/)

[Nico Vibert](https://nicovibert.com/)

[Ryan Kelly](https://www.ryankellysblog.com/)

[Sean Lambert](https://street2clouds.wordpress.com/)

[Christophe Lombard](https://vminded.com/)

[David Zhang](http://davidwzhang.com)

[Sam Akroyd](https://samakroyd.com/)

[Akshay Kalia](https://vmzoneblog.com)