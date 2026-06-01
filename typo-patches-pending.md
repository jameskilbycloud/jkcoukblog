# Typo patches — still pending after WP REST + deploy

_Generated 2026-06-01. Of 338 verified patches, **156 landed live**. The rest are listed below grouped by reason._

## NEVER_APPLIED (105)

❌ Script reported "✅ written" to WP but the old text is still in the rendered body and raw HTML. Means the WP REST POST returned 200 but the change wasn't persisted (WP plugin filter or revision-only save). **Action: edit the post in WP admin and apply manually.**

### `/2017/05/money-saving-uk-version/`  _(1 patch)_

- **Find:** `I currently have a number of UK current accounts`
  **Replace with:** `I currently have a number of UK current accounts.`
  _Why: Missing terminal full stop at end of the paragraph before the next heading/paragraph._


### `/2018/01/lab-storage/`  _(1 patch)_

- **Find:** `I will add some pics when I have tidied up the lab/cables`
  **Replace with:** `I will add some pics when I have tidied up the lab/cables.`
  _Why: Missing terminating full stop at the end of the sentence/paragraph._


### `/2018/01/nutanix-ce/`  _(1 patch)_

- **Find:** `see what was new with AHV and Nutanix CE`
  **Replace with:** `see what was new with AHV and Nutanix CE.`
  _Why: Sentence/paragraph ends without a full stop. Adding the period is the minimal correct fix._


### `/2018/03/aws-for-beginners1/`  _(1 patch)_

- **Find:** `lifting and shifting existing infrastructure into “the cloud”`
  **Replace with:** `lifting and shifting existing infrastructure into “the cloud”.`
  _Why: Missing terminal punctuation. The following paragraph starts a new sentence, confirming this is the end of the prior one._


### `/2018/03/cloudflare/`  _(1 patch)_

- **Find:** `it will automatically purge the cache if required`
  **Replace with:** `it will automatically purge the cache if required.`
  _Why: Missing full stop at end of paragraph/sentence._


### `/2018/12/new-laptop/`  _(1 patch)_

- **Find:** `MacBook Pro’s weren’t worth it`
  **Replace with:** `MacBook Pros weren’t worth it`
  _Why: Incorrect apostrophe; plural 'Pros' should not take a possessive apostrophe._


### `/2019/02/lab-storage-2/`  _(1 patch)_

- **Find:** `I purchased a new Synology DS918`
  **Replace with:** `I purchased a new Synology DS918.`
  _Why: Paragraph ends mid-sentence with no terminating full stop._


### `/2019/12/monitoring-vmc-part-1/`  _(1 patch)_

- **Find:** `It is correctly reporting back that the hosts are running ESXi 6.9.1`
  **Replace with:** `It is correctly reporting back that the hosts are running ESXi 6.9.1.`
  _Why: Missing terminal full stop at end of paragraph — sentence trails off without punctuation._


### `/2020/06/veeamon2020/`  _(2 patches)_

- **Find:** `With that most (if not all IT conferences have been postponed or gone online) Veeam’s annu…`
  **Replace with:** `With that, most (if not all) IT conferences have been postponed or gone online; Veeam’s an…`
  _Why: Opening parenthesis is misplaced — it currently encloses 'if not all IT conferences have been postponed or gone online' instead of just 'if not all'. Fix corrects the parenthetical and the redundant exclamation marks._

- **Find:** `make sure you sign up and view some of the great sessions`
  **Replace with:** `make sure you sign up and view some of the great sessions.`
  _Why: Sentence is missing its terminal full stop._


### `/2020/09/vmc-host-errors/`  _(1 patch)_

- **Find:** `Just another reason why you should look at the VMware Cloud on AWS Service`
  **Replace with:** `Just another reason why you should look at the VMware Cloud on AWS Service.`
  _Why: Final sentence of the post body is missing its closing full stop._


### `/2021/01/my-home-office-setup-upgrades/`  _(4 patches)_

- **Find:** `My Mac is connected via USB-C This helps in reducing the cables on the desk.`
  **Replace with:** `My Mac is connected via USB-C. This helps in reducing the cables on the desk.`
  _Why: Missing full stop after 'USB-C' creates a run-on sentence._

- **Find:** `I have had a variety of Canon SLR’s over the last 14 years and the 5D is certainly the bes…`
  **Replace with:** `I have had a variety of Canon SLRs over the last 14 years and the 5D is certainly the best…`
  _Why: Plural of an acronym (SLRs) should not take an apostrophe, and the comma splice before 'It is' should be a full stop._

- **Find:** `Yes, I snuck in one of the new M1 arm based Mac’s.`
  **Replace with:** `Yes, I snuck in one of the new M1 ARM-based Macs.`
  _Why: ARM is an acronym (should be uppercase, hyphenated as 'ARM-based'); plural 'Macs' should not take an apostrophe._

- **Find:** `*The Beats Solo’s were a gift`
  **Replace with:** `*The Beats Solos were a gift`
  _Why: Plural of the product name 'Solos' should not take a possessive apostrophe._


### `/2022/01/cloudflare-workers-limits-of-the-free-tier/`  _(2 patches)_

- **Find:** `(mainly cosmetic to this site over the last day or so) On most changes`
  **Replace with:** `(mainly cosmetic) to this site over the last day or so. On most changes`
  _Why: Misplaced closing parenthesis and missing full stop create a run-on; logically the parenthetical is just '(mainly cosmetic)'._

- **Find:** `When I next tried to publish I got the following`
  **Replace with:** `When I next tried to publish I got the following:`
  _Why: Missing terminal punctuation before code block; colon is the standard choice when introducing a quoted/coded snippet._


### `/2022/01/lab-update-part-1-compute/`  _(1 patch)_

- **Find:** `One of the Compute nodes was removed from the server`
  **Replace with:** `One of the Compute nodes was removed from the server.`
  _Why: Standalone sentence missing terminal full stop._


### `/2022/01/lab-update-part-2-storage/`  _(2 patches)_

- **Find:** `I will use the 2xGb interfaces for management and the new network for a combination of iSC…`
  **Replace with:** `I will use the 2xGb interfaces for management and the new network for a combination of iSC…`
  _Why: Sentence-ending period is missing._

- **Find:** `This is in addition to my Synology DS918+`
  **Replace with:** `This is in addition to my Synology DS918+.`
  _Why: Sentence-ending period is missing._


### `/2022/01/wrangler-and-node-versions/`  _(1 patch)_

- **Find:** `got the following error message`
  **Replace with:** `got the following error message:`
  _Why: Sentence introducing a code block is missing a terminal colon._


### `/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/`  _(2 patches)_

- **Find:** `The difference is how content is published`
  **Replace with:** `The difference is how content is published.`
  _Why: Missing full stop at end of sentence/paragraph._

- **Find:** `push the relevant content into a GitHub repo`
  **Replace with:** `push the relevant content into a GitHub repo.`
  _Why: Missing full stop at end of sentence/paragraph._


### `/2022/10/starlink/`  _(1 patch)_

- **Find:** `locked down by VMware Corporate IT)`
  **Replace with:** `locked down by VMware Corporate IT).`
  _Why: Missing terminal full stop at the end of a paragraph/sentence._


### `/2022/12/100gb-s-in-my-homelab-sort-of/`  _(1 patch)_

- **Find:** `split the 100’s on the switch into 4×25`
  **Replace with:** `split the 100s on the switch into 4×25`
  _Why: Stray apostrophe on a plural number; 100s is the correct plural form._


### `/2022/12/forcing-an-upgrade-to-vsphere-8/`  _(1 patch)_

- **Find:** `It also listed all of the newly installed VIB’s`
  **Replace with:** `It also listed all of the newly installed VIBs`
  _Why: Greengrocer's apostrophe on plural acronym VIBs._


### `/2022/12/use-portainer-in-a-homelab-with-github/`  _(1 patch)_

- **Find:** `user and user id’s`
  **Replace with:** `user and user IDs`
  _Why: Incorrect apostrophe used for plural of 'ID'; should be 'IDs'._


### `/2023/04/intel-optane/`  _(1 patch)_

- **Find:** `configure the Optane’s as`
  **Replace with:** `configure the Optanes as`
  _Why: Incorrect possessive apostrophe used for a plural — Optanes (plural) does not take an apostrophe._


### `/2023/05/homelab-storage-refresh-part-1/`  _(4 patches)_

- **Find:** `(it was originally called Zettabyte File System) It is a copy-on-write system (COW) If you…`
  **Replace with:** `(it was originally called Zettabyte File System). It is a copy-on-write system (COW). If y…`
  _Why: Two missing full stops between three sentences run together._

- **Find:** `“Data VDEV” This can also be done`
  **Replace with:** `“Data VDEV”. This can also be done`
  _Why: Missing full stop between two sentences after the closing quote of 'Data VDEV'._

- **Find:** `into a “Pool”`
  **Replace with:** `into a “Pool”.`
  _Why: Sentence ends without a full stop._

- **Find:** `When running VM’s sync write is basically essential.`
  **Replace with:** `When running VMs, sync write is basically essential.`
  _Why: 'VM’s' uses a possessive apostrophe for a plural — should be 'VMs'. Also missing comma after the introductory clause._


### `/2023/05/runecast-remediation-scripts/`  _(2 patches)_

- **Find:** `Here you can confirm the discovered issue and the remediation action. ( I have chosen not …`
  **Replace with:** `Here you can confirm the discovered issue and the remediation action. (I have chosen not t…`
  _Why: Stray space after the opening parenthesis and missing full stop inside the parenthetical._

- **Find:** `What an amazing little feature`
  **Replace with:** `What an amazing little feature!`
  _Why: Final exclamatory sentence missing terminal punctuation._


### `/2023/10/vgpu-setup-in-my-homelab/`  _(3 patches)_

- **Find:** `ran the below command to perform the install`
  **Replace with:** `ran the below command to perform the install.`
  _Why: Sentence missing a full stop before the code block._

- **Find:** `all of the memory must be reserved for the VM`
  **Replace with:** `all of the memory must be reserved for the VM.`
  _Why: Sentence missing terminal full stop._

- **Find:** `Using GPU-Z we can validate the resources being presented through to the Virtual Machine`
  **Replace with:** `Using GPU-Z we can validate the resources being presented through to the Virtual Machine.`
  _Why: Sentence missing terminal full stop._


### `/2024/06/unifi-dhcp-option-43/`  _(2 patches)_

- **Find:** `so let me explain. It is made up of 2 parts`
  **Replace with:** `so let me explain. It is made up of 2 parts.`
  _Why: Missing terminating full stop at end of paragraph._

- **Find:** `I am hosting the controller on IP 192.168.20.2 The remaining part`
  **Replace with:** `I am hosting the controller on IP 192.168.20.2. The remaining part`
  _Why: Missing full stop between the IP address and the start of the next sentence — clear run-on._


### `/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/`  _(4 patches)_

- **Find:** `VM running Ubuntu 24.04 VM`
  **Replace with:** `VM running Ubuntu 24.04`
  _Why: Duplicated word 'VM' at the end of the sentence._

- **Find:** `how this much running chat queries may impact things`
  **Replace with:** `how much running chat queries may impact things`
  _Why: Stray extra word 'this' makes the sentence ungrammatical._

- **Find:** `even if its not running any queries`
  **Replace with:** `even if it’s not running any queries`
  _Why: Possessive 'its' used where contraction 'it’s' (it is) is required._

- **Find:** `a bit more of a reminder for me as what I have done`
  **Replace with:** `a bit more of a reminder for me of what I have done`
  _Why: Wrong preposition; 'as' should be 'of' (or 'as to'). Smallest correct change is 'of'._


### `/2024/12/zfs-on-vmware/`  _(5 patches)_

- **Find:** `You also need to do is to to ensure that TrueNAS can see unique disk IDs.`
  **Replace with:** `What you also need to do is to ensure that TrueNAS can see unique disk IDs.`
  _Why: Real grammar error: duplicated word 'to to' and the sentence is missing its subject. Verbatim match in body._

- **Find:** `To confirm that To confirm that trim is working execute the below command command is worki…`
  **Replace with:** `To confirm that trim is working, execute the below command`
  _Why: Clearly broken/garbled text with repeated phrases; appears verbatim in body._

- **Find:** `the VM’s be provisioned with thin disks`
  **Replace with:** `the VMs be provisioned with thin disks`
  _Why: Incorrect possessive apostrophe used for the plural 'VMs'. Verbatim match with curly apostrophe._

- **Find:** `the VMs’s storage used`
  **Replace with:** `the VM’s storage used`
  _Why: Double possessive 'VMs's' is ungrammatical; should be singular possessive 'VM's'. Verbatim match._

- **Find:** `Before and after listed below command`
  **Replace with:** `Before and after listed below.`
  _Why: Stray trailing word 'command' renders the sentence broken/incomplete; needs terminating punctuation._


### `/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/`  _(1 patch)_

- **Find:** `is it generate similar tags`
  **Replace with:** `is that it generates similar tags`
  _Why: Grammar error: verb agreement broken and missing 'that' makes the clause ungrammatical. The smallest correct fix is 'is that it generates similar tags'._


### `/2025/04/warp-the-intelligent-terminal/`  _(8 patches)_

- **Find:** `linux based tools`
  **Replace with:** `Linux-based tools`
  _Why: 'Linux' is a proper noun and must be capitalised; 'Linux-based' is the standard compound modifier._

- **Find:** `self taught`
  **Replace with:** `self-taught`
  _Why: Standard compound adjective requires a hyphen._

- **Find:** `I take some shortcuts that is an acceptable risk`
  **Replace with:** `I take some shortcuts that are an acceptable risk`
  _Why: Subject-verb agreement: plural 'shortcuts' takes 'are', not 'is'._

- **Find:** `Taken from Warps website`
  **Replace with:** `Taken from Warp's website`
  _Why: Missing apostrophe on the possessive 'Warp's'._

- **Find:** `Where the beauty of warp kicked in and said`
  **Replace with:** `Where the beauty of Warp kicked in and said`
  _Why: 'Warp' is a product name and should be capitalised consistently with the rest of the post._

- **Find:** `It then auto executed a cat command`
  **Replace with:** `It then auto-executed a cat command`
  _Why: 'auto-' prefix takes a hyphen when forming a compound verb here._

- **Find:** `asked if it was ok to run it which I approved`
  **Replace with:** `asked if it was OK to run it, which I approved`
  _Why: 'ok' is conventionally capitalised as 'OK'; a comma is needed before the non-restrictive 'which' clause._

- **Find:** `Once apt-get had been upgraded the duplicates were no longer in place`
  **Replace with:** `Once apt-get had been upgraded, the duplicates were no longer in place`
  _Why: Missing comma after the introductory subordinate clause._


### `/2025/05/vmc-quick-sizing-guide/`  _(1 patch)_

- **Find:** `This is based on vSAN OSA and excluding the management overhead (Ie valid for secondary cl…`
  **Replace with:** `This is based on vSAN OSA and excludes the management overhead (i.e. valid for secondary c…`
  _Why: Verb agreement fix ('excluding' -> 'excludes' to pair with 'is based'); 'Ie' should be the standard abbreviation 'i.e.'; missing full stop after the closing parenthesis creates a run-on sentence._


### `/2025/08/vmc-host-deepdive/`  _(1 patch)_

- **Find:** `I have just collated it into a single page`
  **Replace with:** `I have just collated it into a single page.`
  _Why: Sentence ends without a full stop before the next paragraph; adding a period correctly terminates the sentence._


### `/2025/09/managing-my-homelab-with-semaphoreui/`  _(2 patches)_

- **Find:** `It’s possible to have multiple repo’s connected`
  **Replace with:** `It’s possible to have multiple repos connected`
  _Why: Greengrocer's apostrophe in plural — 'repo's' should be 'repos'. The first apostrophe (It's) is correct as a contraction; only the second is wrong._

- **Find:** `I have spun up a Vanilla Ubuntu 24.04 server`
  **Replace with:** `I have spun up a vanilla Ubuntu 24.04 server`
  _Why: 'Vanilla' here is a common adjective meaning plain/standard, not a proper noun, so it should be lowercase mid-sentence._


### `/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/`  _(10 patches)_

- **Find:** `Replaces all WordPress URL’s as relative`
  **Replace with:** `Replaces all WordPress URLs as relative`
  _Why: Stray apostrophe in plural — URLs should not have an apostrophe._

- **Find:** `Set’s up the job on a runner`
  **Replace with:** `Sets up the job on a runner`
  _Why: Wrong apostrophe — verb 'Sets' (3rd-person singular), not possessive._

- **Find:** `Check’s Out the repo`
  **Replace with:** `Checks Out the repo`
  _Why: Wrong apostrophe — verb 'Checks', not possessive._

- **Find:** `Test’s the runner environment`
  **Replace with:** `Tests the runner environment`
  _Why: Wrong apostrophe — verb 'Tests', not possessive._

- **Find:** `Install any relevant dependencies`
  **Replace with:** `Installs any relevant dependencies`
  _Why: Verb agreement — other bullets in the list use 3rd-person singular (Sets, Generates, Notifies, Executes)._

- **Find:** `Commit and Pushes the Static Site`
  **Replace with:** `Commits and Pushes the Static Site`
  _Why: Verb agreement — 'Pushes' is 3rd-person singular so the conjoined verb should be 'Commits'._

- **Find:** `therefore for the GitHub-hosted runner`
  **Replace with:** `therefore not reachable by the GitHub-hosted runner`
  _Why: Sentence is grammatically broken/missing words — current text has no verb after 'therefore'._

- **Find:** `so you can’t instantly view your changes without having any DNS propagation issues`
  **Replace with:** `so you can instantly view your changes without having any DNS propagation issues`
  _Why: 'can’t' contradicts the meaning of the surrounding sentence (the preview URL is described as a useful feature for instant viewing)._

- **Find:** `I can trigger the GitHub runner manually ( It also runs on a Cron schedule)`
  **Replace with:** `I can trigger the GitHub runner manually (it also runs on a Cron schedule).`
  _Why: Stray space after opening paren, unnecessary capitalisation of 'It', and missing terminal full stop._

- **Find:** `Within WordPress changed comments.php to the following`
  **Replace with:** `Within WordPress I changed comments.php to the following`
  _Why: Missing subject 'I' — sentence has no subject for the verb 'changed'._


### `/2025/12/vsan-cluster-shutdown/`  _(2 patches)_

- **Find:** `select “Restart vSAN Services” The workflow will enable them to bring them back into opera…`
  **Replace with:** `select “Restart vSAN Services”. The workflow will bring them back into operation.`
  _Why: Missing full stop after the closing quote produces a run-on, and 'will enable them to bring them back' is redundant/awkward._

- **Find:** `vCentre`
  **Replace with:** `vCenter`
  _Why: VMware's product name is spelled 'vCenter' (proper noun, US spelling is the product name)._


### `/2026/01/web-development-improvements/`  _(6 patches)_

- **Find:** `just incase`
  **Replace with:** `just in case`
  _Why: 'incase' is not a word; should be two words 'in case'._

- **Find:** `This took a long time to get right that were mainly down to ordering problems`
  **Replace with:** `This took a long time to get right; the issues were mainly down to ordering problems`
  _Why: 'that were' has no plural antecedent — the sentence is grammatically broken._

- **Find:** `less DNS lookups`
  **Replace with:** `fewer DNS lookups`
  _Why: DNS lookups are countable; UK and US English alike require 'fewer'._

- **Find:** `“below the fold” This allowed`
  **Replace with:** `“below the fold”. This allowed`
  _Why: Missing full stop after the closing quote creates a run-on sentence._

- **Find:** `As the site is basically in GitOps fashion. I decided`
  **Replace with:** `As the site is basically run in GitOps fashion, I decided`
  _Why: Sentence fragment — 'As the site is basically in GitOps fashion.' is not a complete sentence; needs a comma and continuation._

- **Find:** `Ie (Published: January 06, 2018, Updated: July 10, 2024)`
  **Replace with:** `i.e. (Published: January 06, 2018, Updated: July 10, 2024)`
  _Why: 'Ie' is not a word; should be 'i.e.' (Latin abbreviation for 'that is')._


### `/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/`  _(9 patches)_

- **Find:** `A NVIDIA datacenter Graphics card and associated Host and Guest drivers`
  **Replace with:** `An NVIDIA datacenter graphics card and associated Host and Guest drivers`
  _Why: 'An' is correct before a word beginning with a vowel sound ('NVIDIA' starts with 'en'). 'Graphics' should be lowercase mid-sentence._

- **Find:** `using driver version 535.247.0`
  **Replace with:** `using driver version 535.247.01`
  _Why: Every other reference in the post (driver filename, nvidia-smi output, Variables table) uses 535.247.01; the bare '535.247.0' here is clearly a truncated version string._

- **Find:** `could be more appropriate….`
  **Replace with:** `could be more appropriate.`
  _Why: Ellipsis character followed by an extra full stop; collapse to a single full stop (or just the ellipsis). Current form is malformed punctuation._

- **Find:** `which is the LTS version.` The Driver bundle`
  **Replace with:** `which is the LTS version. The Driver bundle`
  _Why: Stray backtick after the full stop; clearly a markdown/formatting artefact._

- **Find:** `to multiple VM’s`
  **Replace with:** `to multiple VMs`
  _Why: Possessive apostrophe used for a plural. Body uses curly apostrophe, hence the adjusted find._

- **Find:** `vSphere Host and vCentre server`
  **Replace with:** `vSphere Host and vCenter server`
  _Why: VMware's product is officially spelled 'vCenter' (proper noun); UK spelling does not apply to product names._

- **Find:** `vGPU profiles in vCentre.`
  **Replace with:** `vGPU profiles in vCenter.`
  _Why: VMware's product is officially spelled 'vCenter' (proper noun); UK spelling does not apply to product names._

- **Find:** `deploy this as a HTTPS service`
  **Replace with:** `deploy this as an HTTPS service`
  _Why: 'HTTPS' is pronounced 'aitch-tee-tee-pee-ess', starting with a vowel sound, so 'an HTTPS' is correct._

- **Find:** `and the licensing are working correctly`
  **Replace with:** `and the licensing is working correctly`
  _Why: Subject 'the licensing' is singular and requires 'is', not 'are'._


### `/2026/03/octopus-agile-battery-solar-calculator/`  _(4 patches)_

- **Find:** `Givenergy 13.5kWh`
  **Replace with:** `GivEnergy 13.5kWh`
  _Why: Inconsistent brand casing in same sentence; the brand is GivEnergy (matches the immediately preceding instance)._

- **Find:** `if the price of batteries halve and the price of electric doubles`
  **Replace with:** `if the price of batteries halves and the price of electricity doubles`
  _Why: 'electric' should be 'electricity' (noun, not adjective); 'price... halves' agrees with singular subject 'price'._

- **Find:** `( I am £178 better off than a tracker tariff over the last 4 months)`
  **Replace with:** `(I am £178 better off than a tracker tariff over the last 4 months)`
  _Why: Stray space after the opening parenthesis._

- **Find:** `This is an important factor in the calculations`
  **Replace with:** `This is an important factor in the calculations.`
  _Why: Sentence ending the SEG section is missing its terminal full stop._


### `/2026/04/automated-vcf-9-offline-depot/`  _(3 patches)_

- **Find:** `What the script does under the hood is`
  **Replace with:** `What the script does under the hood is:`
  _Why: Missing colon before the numbered list that immediately follows — leaves the sentence dangling._

- **Find:** `You will see something like this in the Traefik logs if you do`
  **Replace with:** `You will see something like this in the Traefik logs if you do:`
  _Why: Missing colon before the code/log block — the sentence dangles._

- **Find:** `SSH into your VM and run`
  **Replace with:** `SSH into your VM and run:`
  _Why: Missing colon before the code block that immediately follows._


### `/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/`  _(6 patches)_

- **Find:** `compose file uses the pattern`
  **Replace with:** `The compose file uses the pattern`
  _Why: Sentence starts with lowercase 'compose' missing the article 'The'; clear grammar error._

- **Find:** `I have allocated container resources as follows`
  **Replace with:** `I have allocated container resources as follows:`
  _Why: Missing colon before what follows (introduces a list/visual)._

- **Find:** `I would also highly recommend the data disk is on NVMe`
  **Replace with:** `I would also highly recommend the data disk is on NVMe.`
  _Why: Missing terminal full stop at end of paragraph before next H2 heading._

- **Find:** `some of it needs protecting`
  **Replace with:** `some of it needs protecting.`
  _Why: Missing terminal full stop at end of paragraph._

- **Find:** `This gives me the ability to restore`
  **Replace with:** `This gives me the ability to restore:`
  _Why: Missing colon — sentence introduces a bulleted list._

- **Find:** `in the .env file GitHub repo URL (e.g.`
  **Replace with:** `in the .env file as the GitHub repo URL (e.g.`
  _Why: Missing 'as the' — without it the noun phrase 'GitHub repo URL' has no grammatical role._


### `/2026/04/new-vmc-host-i7i-metal-24xl/`  _(1 patch)_

- **Find:** `taken from instances website vSAN performance will differ`
  **Replace with:** `taken from the instance's website. vSAN performance will differ`
  _Why: Run-on sentence with missing apostrophe and missing sentence break. Verified in body line 154. This claim supersedes the narrower 'instances website' claim._


### `/2026/04/vsphere-power-management-driven-by-ansible/`  _(2 patches)_

- **Find:** `tedious and who wants to do that.`
  **Replace with:** `tedious — and who wants to do that?`
  _Why: Rhetorical question is punctuated with a full stop; should end with a question mark._

- **Find:** `As I have been using Ansible a lot lately therefore I decided to create two playbooks`
  **Replace with:** `As I have been using Ansible a lot lately, I decided to create two playbooks`
  _Why: 'As...therefore' is redundant/ungrammatical because both 'as' and 'therefore' introduce causation._


### `/lab/`  _(1 patch)_

- **Find:** `with an identical configuration as below`
  **Replace with:** `with an identical configuration as below.`
  _Why: Sentence ends without a full stop._


## TEXT_DRIFTED (35)

🔄 Neither old nor new text is in the body — the surrounding content has been changed by you separately since the audit. **Action: probably nothing — the original typo may already be gone.**

### `/2018/01/lab-storage/`  _(1 patch)_

- **Find:** `I also have a DS216+II Synology with 2x 2TB WD Red’s this is my tier 2 lab storage. for ba…`
  **Replace with:** `I also have a DS216+II Synology with 2x 2TB WD Reds; this is my tier 2 lab storage, for ba…`
  _Why: Run-on sentence with comma splice, lowercase 'for' starting a sentence fragment, and greengrocer's apostrophes in plural Reds/ISOs. Missing terminating full stop._


### `/2018/01/nutanix-ce/`  _(2 patches)_

- **Find:** `the same server I ran initially. a Dell T20 with the Xeon processor 32GB of RAM 1x240GB SS…`
  **Replace with:** `the same server I ran initially: a Dell T20 with the Xeon processor, 32GB of RAM, 1x240GB …`
  _Why: Incorrect full stop creating a sentence fragment, plus missing serial commas between hardware spec items that make the list unreadable._

- **Find:** `Ill post back with some updates of what I get up to with it`
  **Replace with:** `I'll post back with some updates of what I get up to with it.`
  _Why: Missing apostrophe in contraction ('Ill' should be 'I'll') and missing terminal full stop on the sentence._


### `/2018/03/aws-for-beginners1/`  _(1 patch)_

- **Find:** `This is a must, Sadly AWS don’t appear to support my preferred 2FA device. Yubikey so I’m …`
  **Replace with:** `This is a must. Sadly, AWS doesn’t appear to support my preferred 2FA device, the Yubikey,…`
  _Why: Genuine grammar errors: comma splice ('must, Sadly'), subject-verb agreement ('AWS don't' → 'AWS doesn't'), and orphan fragment ('Yubikey so…'). Replacement repairs all three minimally and adds the missing terminal full stop._


### `/2018/03/cloudflare/`  _(1 patch)_

- **Find:** `you input where the real webserver lives cloudflare will do the rest.`
  **Replace with:** `you input where the real webserver lives and Cloudflare will do the rest.`
  _Why: Run-on sentence missing conjunction; also 'cloudflare' should be capitalised as the company name 'Cloudflare' (used capitalised elsewhere in the post)._


### `/2018/06/nutanix-command-reference-guide/`  _(2 patches)_

- **Find:** `Its here as a reference`
  **Replace with:** `It's here as a reference`
  _Why: Missing apostrophe — 'Its' (possessive) should be 'It's' (contraction of 'it is')._

- **Find:** `ill generally add it here`
  **Replace with:** `I'll generally add it here`
  _Why: 'ill' should be the contraction 'I'll' (I will); current form reads as the adjective 'ill'._


### `/2018/10/and-now-for-something-completely-different/`  _(2 patches)_

- **Find:** `I have been lucky enough to be involved with all of these ( some much more than others) Al…`
  **Replace with:** `I have been lucky enough to be involved with all of these (some much more than others). Al…`
  _Why: Stray space after opening parenthesis, missing full stop before 'Although' creating a run-on sentence, and missing comma after 'complete'._

- **Find:** `for professional services in 2018

Yes,`
  **Replace with:** `for professional services in 2018.

Yes,`
  _Why: Sentence ends without a full stop before the new paragraph begins._


### `/2019/01/whats-in-my-backpack/`  _(1 patch)_

- **Find:** `depending on if need to go to a datacenter`
  **Replace with:** `depending on whether I need to go to a datacenter`
  _Why: Missing subject 'I' creates an ungrammatical clause. 'Whether' is also more natural than 'if' here. Real grammar error._


### `/2020/07/nutanix-ncp/`  _(1 patch)_

- **Find:** `All in all top work Nutanix`
  **Replace with:** `All in all, top work Nutanix.`
  _Why: Real punctuation error in the main article body — missing comma after the introductory phrase 'All in all' and missing terminal full stop at the end of the closing sentence._


### `/2021/02/apple-content-caching/`  _(3 patches)_

- **Find:** `MacBook Air

Ipad

iPhone Xs`
  **Replace with:** `MacBook Air

iPad

iPhone XS`
  _Why: Fixes two Apple brand casing errors in the wife's device list: 'Ipad' → 'iPad' and 'iPhone Xs' → 'iPhone XS' (matches the 'iPhone XS' casing used earlier in the same post)._

- **Find:** `the amount of disk space to use it defaults to 10%`
  **Replace with:** `the amount of disk space to use; it defaults to 10%`
  _Why: Run-on sentence joining two independent clauses without punctuation; a semicolon (or full stop) is needed._

- **Find:** `More info on it can be found here

To enable it is very straightforward`
  **Replace with:** `More info on it can be found here.

To enable it is very straightforward:`
  _Why: Both sentences are missing terminal punctuation — the first needs a full stop and the second needs a colon to introduce the steps that follow._


### `/2022/01/lab-update-part-2-storage/`  _(1 patch)_

- **Find:** `TrueNas is the successor to FreeNas a very popular BSD based StorageOS and TrueNas scale i…`
  **Replace with:** `TrueNAS is the successor to FreeNAS, a very popular BSD-based storage OS, and TrueNAS Scal…`
  _Why: TrueNAS and FreeNAS are the canonical product spellings (uppercase NAS); a comma is needed after the appositive, and 'TrueNas scale' should be the product name 'TrueNAS Scale'._


### `/2022/01/wrangler-and-node-versions/`  _(1 patch)_

- **Find:** `all of my Mac’s I typically just upgrade`
  **Replace with:** `all of my Macs. I typically just upgrade`
  _Why: Apostrophe used for a plural ('Mac’s' should be 'Macs') and a missing sentence boundary before 'I typically' creating a run-on._


### `/2022/12/use-portainer-in-a-homelab-with-github/`  _(2 patches)_

- **Find:** `Plus have GitHub (or similar) version control system`
  **Replace with:** `Plus, have a GitHub (or similar) version control system`
  _Why: Missing article 'a' and missing comma after 'Plus'; sentence is ungrammatical as written._

- **Find:** `a great blog on this can be found here
`
  **Replace with:** `a great blog on this can be found here.
`
  _Why: Sentence ends without a full stop before the next paragraph._


### `/2023/04/intel-optane/`  _(1 patch)_

- **Find:** `some back to back test to showcase`
  **Replace with:** `some back-to-back tests to showcase`
  _Why: 'back-to-back' is a compound adjective requiring hyphens, and 'test' should be plural 'tests' to agree with 'some'._


### `/2023/05/homelab-storage-refresh-part-1/`  _(2 patches)_

- **Find:** `Im sure there optimisations`
  **Replace with:** `I'm sure there are optimisations`
  _Why: Missing apostrophe in 'Im' and missing 'are' between 'there' and 'optimisations'. Both are clear grammatical errors._

- **Find:** `of 1095 TBW
`
  **Replace with:** `of 1095 TBW.
`
  _Why: Sentence ends without a full stop before the next section heading._


### `/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/`  _(2 patches)_

- **Find:** `As business demands lower RPO’s any improvement`
  **Replace with:** `As business demands lower RPOs, any improvement`
  _Why: Apostrophe-plural is wrong, and a comma is needed after the introductory clause to avoid a run-on._

- **Find:** `It is also not currently available in a 2-node or Stretched SDDC configuration
`
  **Replace with:** `It is also not currently available in a 2-node or Stretched SDDC configuration.
`
  _Why: Sentence at end of paragraph is missing its terminating full stop._


### `/2024/01/multihost-holodeck-vcf/`  _(1 patch)_

- **Find:** `The CPU’s in my hosts were identical.`
  **Replace with:** `The CPUs in my hosts were identical.`
  _Why: Plural of CPU is CPUs; the apostrophe is incorrect for a plural (greengrocer’s apostrophe)._


### `/2024/06/unifi-dhcp-option-43/`  _(1 patch)_

- **Find:** `I can connect a factory fresh UniFi device to my network DHCP will hand out an IP`
  **Replace with:** `I can connect a factory-fresh UniFi device to my network; DHCP will hand out an IP`
  _Why: Run-on sentence — 'network' and 'DHCP will hand out' need separating punctuation. 'factory-fresh' as a compound adjective also takes a hyphen._


### `/2025/04/warp-the-intelligent-terminal/`  _(2 patches)_

- **Find:** `Sometimes you just need a helping hand

Enter Warp`
  **Replace with:** `Sometimes you just need a helping hand.

Enter Warp`
  _Why: Sentence is missing its terminating full stop before the paragraph break._

- **Find:** `sign up with my referral link here

Connect with me`
  **Replace with:** `sign up with my referral link here.

Connect with me`
  _Why: Final sentence of the conclusion is missing its terminating full stop._


### `/2025/12/vsan-cluster-shutdown/`  _(1 patch)_

- **Find:** `How to safety shutdown a vSAN Environment`
  **Replace with:** `How to safely shut down a vSAN Environment`
  _Why: 'safety' is a noun being used where the adverb 'safely' is required; 'shutdown' is a noun, the verb form is 'shut down'. Both are clear grammatical errors. [Lives in the WP excerpt field of the source post, not body.]_


### `/2026/01/web-development-improvements/`  _(1 patch)_

- **Find:** `preconnect for plausible.jameskilby.cloud
`
  **Replace with:** `preconnect for plausible.jameskilby.cloud.
`
  _Why: Sentence ends without a full stop before the next paragraph._


### `/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/`  _(2 patches)_

- **Find:** `automating these prerequisites here

If you have followed along`
  **Replace with:** `automating these prerequisites here.

If you have followed along`
  _Why: Sentence ends without a full stop before the next paragraph begins. Adding the period without changing surrounding text._

- **Find:** `where I added a new model in Ollama it auto detected`
  **Replace with:** `where I added a new model in Ollama and it auto-detected`
  _Why: Run-on clause missing a conjunction, and 'auto detected' should be hyphenated as a compound verb._


### `/2026/03/octopus-agile-battery-solar-calculator/`  _(1 patch)_

- **Find:** `recommend the most cost effective setup.I was surprised`
  **Replace with:** `recommend the most cost-effective setup. I was surprised`
  _Why: Missing space after the full stop; 'cost-effective' is hyphenated as a compound modifier._


### `/2026/04/vsphere-power-management-driven-by-ansible/`  _(2 patches)_

- **Find:** `leverages P-states aggressively that govern frequency and voltage scaling. while preservin…`
  **Replace with:** `leverages P-states aggressively, which govern frequency and voltage scaling, while preserv…`
  _Why: Stray full stop mid-sentence breaks the grammar; replacement uses commas to form a coherent sentence._

- **Find:** `By automating you get a repeatable, process that runs in seconds`
  **Replace with:** `By automating, you get a repeatable process that runs in seconds`
  _Why: Misplaced comma between 'repeatable' and 'process' breaks the noun phrase; missing comma after the introductory clause 'By automating'._


### `/media/`  _(1 patch)_

- **Find:** `You can find me on/in the following Videos/Podcasts
`
  **Replace with:** `You can find me on/in the following Videos/Podcasts.
`
  _Why: Missing terminating full stop at the end of the sentence/paragraph._


## FIND_NOT_IN_RAW_UNKNOWN (33)

❓ Old text in body but not in raw HTML — possibly auto-generated content (excerpt/preview) that mirrors the actual source elsewhere. **Action: inspect.**

### `/2018/03/aws-for-beginners1/`  _(1 patch)_

- **Find:** `Enable Billing Alerts Create an alert so that if your bill is over X you will get a notifi…`
  **Replace with:** `Enable Billing Alerts — create an alert so that if your bill is over X you will get a noti…`
  _Why: Two sentences run together with no punctuation. The sibling bullets above use ' – ' to separate label from explanation; adding an em-dash matches that pattern and fixes the run-on._


### `/2018/05/aws-status-page-monitoring-included/`  _(2 patches)_

- **Find:** `at effectively zero cost`
  **Replace with:** `at effectively zero cost.`
  _Why: The paragraph ends mid-sentence with no full stop; adding the period closes the sentence._

- **Find:** `is documented in the Git repo here`
  **Replace with:** `is documented in the Git repo here.`
  _Why: The sentence under 'Site Response' ends without a full stop._


### `/2018/12/new-laptop/`  _(1 patch)_

- **Find:** `another MacBook Air .`
  **Replace with:** `another MacBook Air.`
  _Why: Stray space before the full stop._


### `/2019/12/monitoring-vmc-part-1/`  _(1 patch)_

- **Find:** `Veeam One .`
  **Replace with:** `Veeam One.`
  _Why: Stray space before the full stop — clear typographical error._


### `/2020/06/veeamon2020/`  _(1 patch)_

- **Find:** `Yes Veeam Backup Agent for MAC`
  **Replace with:** `Yes — Veeam Backup Agent for Mac.`
  _Why: Missing punctuation after 'Yes', and 'Mac' is a product name not an acronym — it should not be all caps._


### `/2020/09/vmware-certified-master-specialist-hci-2020/`  _(1 patch)_

- **Find:** `a VMware Master Services Competency .`
  **Replace with:** `a VMware Master Services Competency.`
  _Why: Stray space between the linked phrase 'VMware Master Services Competency' and the full stop. Removing the space gives the correct punctuation._


### `/2020/12/my-first-pull/`  _(1 patch)_

- **Find:** `listed as a contributor here .`
  **Replace with:** `listed as a contributor here.`
  _Why: Stray space before the full stop is a clear punctuation error._


### `/2022/01/cloudflare-workers-limits-of-the-free-tier/`  _(1 patch)_

- **Find:** `Detailed info on the limits is published here`
  **Replace with:** `Detailed info on the limits is published here.`
  _Why: Sentence is missing its terminating full stop._


### `/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/`  _(2 patches)_

- **Find:** `or can even be run just on your workstation/laptop using local .`
  **Replace with:** `or can even be run just on your workstation/laptop using local).`
  _Why: Opening parenthesis is never closed and the sentence has a stray space before the period; closing the bracket fixes the broken parenthetical._

- **Find:** `I have chosen to keep WordPress running in some docker containers on my Synology`
  **Replace with:** `I have chosen to keep WordPress running in some Docker containers on my Synology.`
  _Why: Missing full stop; 'Docker' is a product name and should be capitalised._


### `/2022/12/use-portainer-in-a-homelab-with-github/`  _(2 patches)_

- **Find:** `Docker and Portainer It’s also important`
  **Replace with:** `Docker and Portainer. It’s also important`
  _Why: Run-on sentence; missing full stop between 'Portainer' and 'It’s'._

- **Find:** `as documented here .`
  **Replace with:** `as documented here.`
  _Why: Stray space before the full stop._


### `/2023/05/homelab-storage-refresh-part-1/`  _(1 patch)_

- **Find:** `2200 MB/s write Some crazy numbers`
  **Replace with:** `2200 MB/s write. Some crazy numbers`
  _Why: Run-on sentence — missing full stop between 'write' and the new sentence 'Some crazy numbers'._


### `/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/`  _(1 patch)_

- **Find:** `If you have not done this ( Or installed the Cloudflare Pages App in GitHub you can do thi…`
  **Replace with:** `If you have not done this (or installed the Cloudflare Pages App in GitHub) you can do thi…`
  _Why: Unclosed parenthesis and incorrectly capitalised 'Or' mid-sentence._


### `/2023/10/going-out-with-a-bang/`  _(1 patch)_

- **Find:** `I decided to give mine to the RNLI .`
  **Replace with:** `I decided to give mine to the RNLI.`
  _Why: Stray space before the full stop after 'RNLI'._


### `/2023/10/vgpu-setup-in-my-homelab/`  _(1 patch)_

- **Find:** `The other node was going to be used as a Tdarr Node`
  **Replace with:** `The other node was going to be used as a Tdarr Node.`
  _Why: End-of-paragraph sentence missing terminal full stop._


### `/2024/01/holodeck-cpu-fixes/`  _(1 patch)_

- **Find:** `deployment script and that is available here`
  **Replace with:** `deployment script, and it is available here.`
  _Why: Missing terminal full stop, and awkward 'and that is' phrasing; small punctuation/wording fix._


### `/2024/01/multihost-holodeck-vcf/`  _(1 patch)_

- **Find:** `All of the storage is to be presented by my TrueNas setup.`
  **Replace with:** `All of the storage is to be presented by my TrueNAS setup.`
  _Why: The product name is officially TrueNAS (all-caps NAS), analogous to vCenter — this is a product-name correction, not a stylistic change._


### `/2024/06/unifi-dhcp-option-43/`  _(1 patch)_

- **Find:** `A multitude of tools exist for converting IP to HEX one can be found here`
  **Replace with:** `A multitude of tools exist for converting IP to HEX; one can be found here.`
  _Why: Run-on sentence with no punctuation between 'HEX' and 'one can be found here'; also missing terminal full stop._


### `/2024/07/new-nodes/`  _(1 patch)_

- **Find:** `To reset the password’s I resorted to using the IPMItool`
  **Replace with:** `To reset the passwords I resorted to using the IPMItool`
  _Why: Incorrect possessive apostrophe in plural 'passwords'._


### `/2025/05/vmc-quick-sizing-guide/`  _(1 patch)_

- **Find:** `For up to date info always use the official sizing tool located here`
  **Replace with:** `For up-to-date info, always use the official sizing tool located here.`
  _Why: 'up to date' is a compound adjective modifying 'info' and requires hyphens; a comma after the introductory phrase improves readability; the sentence is missing its terminal full stop, which would otherwise run into the next sentence._


### `/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/`  _(1 patch)_

- **Find:** `The benefits of this setup I have discussed previously`
  **Replace with:** `The benefits of this setup I have discussed previously.`
  _Why: Missing terminal full stop at end of sentence/paragraph._


### `/2026/01/web-development-improvements/`  _(1 patch)_

- **Find:** `build timestamps When querying`
  **Replace with:** `build timestamps. When querying`
  _Why: Missing full stop creates a run-on sentence between two distinct clauses._


### `/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/`  _(4 patches)_

- **Find:** `the underlying Infrastructure .`
  **Replace with:** `the underlying infrastructure.`
  _Why: Mid-sentence common noun should be lowercase, and there is a stray space before the full stop._

- **Find:** `on my own hardware .`
  **Replace with:** `on my own hardware.`
  _Why: Stray space before the full stop._

- **Find:** `subdomain of your base DOMAIN .`
  **Replace with:** `subdomain of your base DOMAIN.`
  _Why: Stray space before the full stop after DOMAIN._

- **Find:** `spoken around this journey at VMUG`
  **Replace with:** `spoken about this journey at VMUG`
  _Why: 'Spoken around' is incorrect phrasing; 'spoken about' is the natural form._


### `/2026/04/automated-vcf-9-offline-depot/`  _(1 patch)_

- **Find:** `process documented here .`
  **Replace with:** `process documented here.`
  _Why: Stray space before the full stop; the period should be attached to 'here'._


### `/2026/04/new-vmc-host-i7i-metal-24xl/`  _(2 patches)_

- **Find:** `with SCFS via VLR .`
  **Replace with:** `with SCFS via VLR.`
  _Why: Stray space before full stop. Verified in body line 150._

- **Find:** `can be found here .`
  **Replace with:** `can be found here.`
  _Why: Stray space before full stop. Verified in body line 204._


### `/lab/`  _(1 patch)_

- **Find:** `More details are here`
  **Replace with:** `More details are here.`
  _Why: End of Primary Storage paragraph is missing terminal full stop._


### `/media/`  _(1 patch)_

- **Find:** `the Xtravirt CloudInsiders podcast ,`
  **Replace with:** `the Xtravirt CloudInsiders podcast,`
  _Why: Stray space before the comma — punctuation error._


## SPANS_LINK (7)

🔗 The find string spans an `<a>` link tag in the WP source. String matching can't bridge HTML markup. **Action: edit in WP admin — usually a missing full stop after a linked word.**

### `/2018/03/aws-for-beginners1/`  _(1 patch)_

- **Find:** `go and set up an account and play`
  **Replace with:** `go and set up an account and play.`
  _Why: Missing terminal full stop on a paragraph-final sentence._


### `/2018/05/aws-status-page-monitoring-included/`  _(1 patch)_

- **Find:** `The tool I deployed lambstatus supports pulling metrics`
  **Replace with:** `The tool I deployed, lambstatus, supports pulling metrics`
  _Why: 'lambstatus' is an appositive naming the tool and requires commas around it for correct grammar._


### `/2018/12/new-laptop/`  _(1 patch)_

- **Find:** `benefits of the T2 Security chip`
  **Replace with:** `benefits of the T2 Security chip.`
  _Why: Sentence ends without a full stop before the paragraph break._


### `/2023/04/intel-optane/`  _(1 patch)_

- **Find:** `I was lucky enough to get some together with Gareth Edwards we decided to put something to…`
  **Replace with:** `I was lucky enough to get some. Together with Gareth Edwards, we decided to put something …`
  _Why: Two independent clauses run together with no punctuation — splitting into two sentences fixes the run-on._


### `/2023/10/vgpu-setup-in-my-homelab/`  _(1 patch)_

- **Find:** `My Folding@home stats can be seen here and consider joining your compute to the project as…`
  **Replace with:** `My Folding@home stats can be seen here, and consider joining your compute to the project a…`
  _Why: Two independent clauses joined without a comma and missing terminal full stop._


### `/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/`  _(1 patch)_

- **Find:** `connected it to my existing Ollama setup This means that`
  **Replace with:** `connected it to my existing Ollama setup. This means that`
  _Why: Two sentences run together with no full stop between 'setup' and 'This'. Adding a period creates two correct sentences._


### `/about-me/`  _(1 patch)_

- **Find:** `I have been a vExpert for the last 12 years and previously and has been honoured to be awa…`
  **Replace with:** `I have been a vExpert for the last 12 years and have previously been honoured to be awarde…`
  _Why: Real grammar error: duplicate 'and' plus subject-verb agreement issue ('has' should be 'have' to match subject 'I'). The fix removes the duplicate 'and' and corrects the verb form._


## SPANS_OTHER_MARKUP (2)

🔧 The find string spans some other HTML markup. **Action: edit in WP admin.**

### `/2018/01/lab-storage/`  _(1 patch)_

- **Find:** `I have the 4 Nics split into two LACP bonds.`
  **Replace with:** `I have the 4 NICs split into two LACP bonds.`
  _Why: NIC is an acronym (Network Interface Card) and should be capitalised as 'NICs'. Consistent with '4x 1Gb/s NIC' earlier in the post._


### `/2020/06/veeamon2020/`  _(1 patch)_

- **Find:** `Charles Darwin “ It is not the strongest of the species that survives`
  **Replace with:** `Charles Darwin: “It is not the strongest of the species that survives`
  _Why: Stray space after the opening curly quote and the quote needs a colon to introduce it._

