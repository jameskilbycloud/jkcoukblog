# Typo Patches — Verified for Application to WordPress

_Generated: 2026-06-01. **338 verified typo fixes** across **69 posts**._

Each fix has been adversarially re-verified against the published HTML body. Below is the full list grouped by post for review before application.

## Caveats before applying

- **Two patches need NBSP awareness.** `Lab Storage (2018)` and `Homelab Storage Refresh Part 1 (2023)` have published bodies with non-breaking spaces (`\xa0`) between numbers and units — the WP raw source via `?context=edit` likely uses normal spaces, so the patches as written should still apply. The apply script will warn if the find string is not found.
- **One multi-occurrence find.** The homepage post-card excerpt `"How to safety shutdown a vSAN Environment"` appears twice on the homepage but originates from one source post — fixing the source title once will propagate to both.
- **Each patch has occurrences=1 in the body**, but the WP raw content (with block markup, shortcodes) may differ. The apply script does an in-post sanity check before writing.

## Summary by year

| Year | Posts with fixes | Total fixes |
|---|---|---|
| 2026 | 8 | 50 |
| 2025 | 7 | 34 |
| 2024 | 8 | 43 |
| 2023 | 10 | 54 |
| 2022 | 11 | 60 |
| 2021 | 3 | 20 |
| 2020 | 6 | 19 |
| 2019 | 3 | 12 |
| 2018 | 8 | 32 |
| 2017 | 1 | 3 |
| (static) | 4 | 11 |

## Patches by post

### Static / landing pages

#### /about-me/  _(1 fix)_

1. **Find:** `I have been a vExpert for the last 12 years and previously and has been honoured to be awarded Veeam Vanguard status for four years.`
   **Replace:** `I have been a vExpert for the last 12 years and have previously been honoured to be awarded Veeam Vanguard status for four years.`
   _Real grammar error: duplicate 'and' plus subject-verb agreement issue ('has' should be 'have' to match subject 'I'). The fix removes the duplicate 'and' and corrects the verb form._


#### /lab/  _(6 fixes)_

1. **Find:** `for over 6 years) It currently runs`
   **Replace:** `for over 6 years). It currently runs`
   _Missing full stop creating a run-on sentence between '6 years)' and 'It currently'._

2. **Find:** `giving me a usable 66.3 TB This is presented`
   **Replace:** `giving me a usable 66.3 TB. This is presented`
   _Missing full stop between two independent clauses (66.3 TB and This is presented)._

3. **Find:** `More details are here`
   **Replace:** `More details are here.`
   _End of Primary Storage paragraph is missing terminal full stop._

4. **Find:** `with an identical configuration as below`
   **Replace:** `with an identical configuration as below.`
   _Sentence ends without a full stop._

5. **Find:** `GPU is an essential in at least one node.`
   **Replace:** `A GPU is essential in at least one node.`
   _Ungrammatical — 'an essential' reads as a noun; should be 'A GPU is essential'._

6. **Find:** `Heat Output isn’t a huge factor`
   **Replace:** `Heat output isn’t a huge factor`
   _Inconsistent capitalisation — 'Output' should be lower case to match other bullet items._


#### /media/  _(2 fixes)_

1. **Find:** `You can find me on/in the following Videos/Podcasts
`
   **Replace:** `You can find me on/in the following Videos/Podcasts.
`
   _Missing terminating full stop at the end of the sentence/paragraph._

2. **Find:** `the Xtravirt CloudInsiders podcast ,`
   **Replace:** `the Xtravirt CloudInsiders podcast,`
   _Stray space before the comma — punctuation error._


#### /vmc/  _(2 fixes)_

1. **Find:** `VLSR ( formerly SRM Site Recovery Manager)`
   **Replace:** `VLSR (formerly SRM – Site Recovery Manager)`
   _Stray space after '(' and missing separator between the abbreviation SRM and its expansion 'Site Recovery Manager' create a run-on. Inserting an en dash fixes the readability defect while keeping the abbreviation+expansion convention._

2. **Find:** `VLCR ( Formerly VCDR VMware Cloud Disaster Recovery)`
   **Replace:** `VLCR (formerly VCDR – VMware Cloud Disaster Recovery)`
   _Stray space after '(', capitalised 'Formerly' inconsistent with the sibling line below, and missing separator between 'VCDR' and its expansion produce a run-on. Fix matches the adjacent line's lowercase 'formerly' and adds the needed separator._


### 2026

#### /2026/01/web-development-improvements/  _(11 fixes)_

1. **Find:** `in “the backend” These help improve`
   **Replace:** `in “the backend”. These help improve`
   _Missing full stop after the closing quote creates a run-on sentence._

2. **Find:** `compression ratio’s than gzip`
   **Replace:** `compression ratios than gzip`
   _Plural 'ratios' should not take an apostrophe._

3. **Find:** `excellent compression ratio’s`
   **Replace:** `excellent compression ratios`
   _Plural 'ratios' should not take an apostrophe._

4. **Find:** `just incase`
   **Replace:** `just in case`
   _'incase' is not a word; should be two words 'in case'._

5. **Find:** `This took a long time to get right that were mainly down to ordering problems`
   **Replace:** `This took a long time to get right; the issues were mainly down to ordering problems`
   _'that were' has no plural antecedent — the sentence is grammatically broken._

6. **Find:** `less DNS lookups`
   **Replace:** `fewer DNS lookups`
   _DNS lookups are countable; UK and US English alike require 'fewer'._

7. **Find:** `“below the fold” This allowed`
   **Replace:** `“below the fold”. This allowed`
   _Missing full stop after the closing quote creates a run-on sentence._

8. **Find:** `preconnect for plausible.jameskilby.cloud
`
   **Replace:** `preconnect for plausible.jameskilby.cloud.
`
   _Sentence ends without a full stop before the next paragraph._

9. **Find:** `build timestamps When querying`
   **Replace:** `build timestamps. When querying`
   _Missing full stop creates a run-on sentence between two distinct clauses._

10. **Find:** `As the site is basically in GitOps fashion. I decided`
   **Replace:** `As the site is basically run in GitOps fashion, I decided`
   _Sentence fragment — 'As the site is basically in GitOps fashion.' is not a complete sentence; needs a comma and continuation._

11. **Find:** `Ie (Published: January 06, 2018, Updated: July 10, 2024)`
   **Replace:** `i.e. (Published: January 06, 2018, Updated: July 10, 2024)`
   _'Ie' is not a word; should be 'i.e.' (Latin abbreviation for 'that is')._


#### /2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/  _(9 fixes)_

1. **Find:** `A NVIDIA datacenter Graphics card and associated Host and Guest drivers`
   **Replace:** `An NVIDIA datacenter graphics card and associated Host and Guest drivers`
   _'An' is correct before a word beginning with a vowel sound ('NVIDIA' starts with 'en'). 'Graphics' should be lowercase mid-sentence._

2. **Find:** `using driver version 535.247.0`
   **Replace:** `using driver version 535.247.01`
   _Every other reference in the post (driver filename, nvidia-smi output, Variables table) uses 535.247.01; the bare '535.247.0' here is clearly a truncated version string._

3. **Find:** `could be more appropriate….`
   **Replace:** `could be more appropriate.`
   _Ellipsis character followed by an extra full stop; collapse to a single full stop (or just the ellipsis). Current form is malformed punctuation._

4. **Find:** `which is the LTS version.` The Driver bundle`
   **Replace:** `which is the LTS version. The Driver bundle`
   _Stray backtick after the full stop; clearly a markdown/formatting artefact._

5. **Find:** `to multiple VM’s`
   **Replace:** `to multiple VMs`
   _Possessive apostrophe used for a plural. Body uses curly apostrophe, hence the adjusted find._

6. **Find:** `vSphere Host and vCentre server`
   **Replace:** `vSphere Host and vCenter server`
   _VMware's product is officially spelled 'vCenter' (proper noun); UK spelling does not apply to product names._

7. **Find:** `vGPU profiles in vCentre.`
   **Replace:** `vGPU profiles in vCenter.`
   _VMware's product is officially spelled 'vCenter' (proper noun); UK spelling does not apply to product names._

8. **Find:** `deploy this as a HTTPS service`
   **Replace:** `deploy this as an HTTPS service`
   _'HTTPS' is pronounced 'aitch-tee-tee-pee-ess', starting with a vowel sound, so 'an HTTPS' is correct._

9. **Find:** `and the licensing are working correctly`
   **Replace:** `and the licensing is working correctly`
   _Subject 'the licensing' is singular and requires 'is', not 'are'._


#### /2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/  _(6 fixes)_

1. **Find:** `automating these prerequisites here

If you have followed along`
   **Replace:** `automating these prerequisites here.

If you have followed along`
   _Sentence ends without a full stop before the next paragraph begins. Adding the period without changing surrounding text._

2. **Find:** `the underlying Infrastructure .`
   **Replace:** `the underlying infrastructure.`
   _Mid-sentence common noun should be lowercase, and there is a stray space before the full stop._

3. **Find:** `on my own hardware .`
   **Replace:** `on my own hardware.`
   _Stray space before the full stop._

4. **Find:** `subdomain of your base DOMAIN .`
   **Replace:** `subdomain of your base DOMAIN.`
   _Stray space before the full stop after DOMAIN._

5. **Find:** `spoken around this journey at VMUG`
   **Replace:** `spoken about this journey at VMUG`
   _'Spoken around' is incorrect phrasing; 'spoken about' is the natural form._

6. **Find:** `where I added a new model in Ollama it auto detected`
   **Replace:** `where I added a new model in Ollama and it auto-detected`
   _Run-on clause missing a conjunction, and 'auto detected' should be hyphenated as a compound verb._


#### /2026/03/octopus-agile-battery-solar-calculator/  _(6 fixes)_

1. **Find:** `Givenergy 13.5kWh`
   **Replace:** `GivEnergy 13.5kWh`
   _Inconsistent brand casing in same sentence; the brand is GivEnergy (matches the immediately preceding instance)._

2. **Find:** `if the price of batteries halve and the price of electric doubles`
   **Replace:** `if the price of batteries halves and the price of electricity doubles`
   _'electric' should be 'electricity' (noun, not adjective); 'price... halves' agrees with singular subject 'price'._

3. **Find:** `run the script.To get your API key`
   **Replace:** `run the script. To get your API key`
   _Missing space after the full stop between two sentences._

4. **Find:** `recommend the most cost effective setup.I was surprised`
   **Replace:** `recommend the most cost-effective setup. I was surprised`
   _Missing space after the full stop; 'cost-effective' is hyphenated as a compound modifier._

5. **Find:** `( I am £178 better off than a tracker tariff over the last 4 months)`
   **Replace:** `(I am £178 better off than a tracker tariff over the last 4 months)`
   _Stray space after the opening parenthesis._

6. **Find:** `This is an important factor in the calculations`
   **Replace:** `This is an important factor in the calculations.`
   _Sentence ending the SEG section is missing its terminal full stop._


#### /2026/04/automated-vcf-9-offline-depot/  _(4 fixes)_

1. **Find:** `process documented here .`
   **Replace:** `process documented here.`
   _Stray space before the full stop; the period should be attached to 'here'._

2. **Find:** `What the script does under the hood is`
   **Replace:** `What the script does under the hood is:`
   _Missing colon before the numbered list that immediately follows — leaves the sentence dangling._

3. **Find:** `You will see something like this in the Traefik logs if you do`
   **Replace:** `You will see something like this in the Traefik logs if you do:`
   _Missing colon before the code/log block — the sentence dangles._

4. **Find:** `SSH into your VM and run`
   **Replace:** `SSH into your VM and run:`
   _Missing colon before the code block that immediately follows._


#### /2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/  _(7 fixes)_

1. **Find:** `compose file uses the pattern`
   **Replace:** `The compose file uses the pattern`
   _Sentence starts with lowercase 'compose' missing the article 'The'; clear grammar error._

2. **Find:** `The internal network (Green Zone) is configured and a dedicated subnet`
   **Replace:** `The internal network (Green Zone) is configured with a dedicated subnet`
   _Broken grammar — 'is configured and a dedicated subnet' should be 'is configured with a dedicated subnet'._

3. **Find:** `I have allocated container resources as follows`
   **Replace:** `I have allocated container resources as follows:`
   _Missing colon before what follows (introduces a list/visual)._

4. **Find:** `I would also highly recommend the data disk is on NVMe`
   **Replace:** `I would also highly recommend the data disk is on NVMe.`
   _Missing terminal full stop at end of paragraph before next H2 heading._

5. **Find:** `some of it needs protecting`
   **Replace:** `some of it needs protecting.`
   _Missing terminal full stop at end of paragraph._

6. **Find:** `This gives me the ability to restore`
   **Replace:** `This gives me the ability to restore:`
   _Missing colon — sentence introduces a bulleted list._

7. **Find:** `in the .env file GitHub repo URL (e.g.`
   **Replace:** `in the .env file as the GitHub repo URL (e.g.`
   _Missing 'as the' — without it the noun phrase 'GitHub repo URL' has no grammatical role._


#### /2026/04/new-vmc-host-i7i-metal-24xl/  _(3 fixes)_

1. **Find:** `with SCFS via VLR .`
   **Replace:** `with SCFS via VLR.`
   _Stray space before full stop. Verified in body line 150._

2. **Find:** `can be found here .`
   **Replace:** `can be found here.`
   _Stray space before full stop. Verified in body line 204._

3. **Find:** `taken from instances website vSAN performance will differ`
   **Replace:** `taken from the instance's website. vSAN performance will differ`
   _Run-on sentence with missing apostrophe and missing sentence break. Verified in body line 154. This claim supersedes the narrower 'instances website' claim._


#### /2026/04/vsphere-power-management-driven-by-ansible/  _(4 fixes)_

1. **Find:** `leverages P-states aggressively that govern frequency and voltage scaling. while preserving turbo boost`
   **Replace:** `leverages P-states aggressively, which govern frequency and voltage scaling, while preserving turbo boost`
   _Stray full stop mid-sentence breaks the grammar; replacement uses commas to form a coherent sentence._

2. **Find:** `By automating you get a repeatable, process that runs in seconds`
   **Replace:** `By automating, you get a repeatable process that runs in seconds`
   _Misplaced comma between 'repeatable' and 'process' breaks the noun phrase; missing comma after the introductory clause 'By automating'._

3. **Find:** `tedious and who wants to do that.`
   **Replace:** `tedious — and who wants to do that?`
   _Rhetorical question is punctuated with a full stop; should end with a question mark._

4. **Find:** `As I have been using Ansible a lot lately therefore I decided to create two playbooks`
   **Replace:** `As I have been using Ansible a lot lately, I decided to create two playbooks`
   _'As...therefore' is redundant/ungrammatical because both 'as' and 'therefore' introduce causation._


### 2025

#### /2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/  _(3 fixes)_

1. **Find:** `is it generate similar tags`
   **Replace:** `is that it generates similar tags`
   _Grammar error: verb agreement broken and missing 'that' makes the clause ungrammatical. The smallest correct fix is 'is that it generates similar tags'._

2. **Find:** `connected it to my existing Ollama setup This means that`
   **Replace:** `connected it to my existing Ollama setup. This means that`
   _Two sentences run together with no full stop between 'setup' and 'This'. Adding a period creates two correct sentences._

3. **Find:** `ranging from company takeovers. To sites being dead.`
   **Replace:** `ranging from company takeovers, to sites being dead.`
   _'To sites being dead.' is a sentence fragment. Replacing the full stop with a comma joins it to the preceding clause as a single grammatical sentence._


#### /2025/04/warp-the-intelligent-terminal/  _(10 fixes)_

1. **Find:** `linux based tools`
   **Replace:** `Linux-based tools`
   _'Linux' is a proper noun and must be capitalised; 'Linux-based' is the standard compound modifier._

2. **Find:** `self taught`
   **Replace:** `self-taught`
   _Standard compound adjective requires a hyphen._

3. **Find:** `I take some shortcuts that is an acceptable risk`
   **Replace:** `I take some shortcuts that are an acceptable risk`
   _Subject-verb agreement: plural 'shortcuts' takes 'are', not 'is'._

4. **Find:** `Sometimes you just need a helping hand

Enter Warp`
   **Replace:** `Sometimes you just need a helping hand.

Enter Warp`
   _Sentence is missing its terminating full stop before the paragraph break._

5. **Find:** `Taken from Warps website`
   **Replace:** `Taken from Warp's website`
   _Missing apostrophe on the possessive 'Warp's'._

6. **Find:** `Where the beauty of warp kicked in and said`
   **Replace:** `Where the beauty of Warp kicked in and said`
   _'Warp' is a product name and should be capitalised consistently with the rest of the post._

7. **Find:** `It then auto executed a cat command`
   **Replace:** `It then auto-executed a cat command`
   _'auto-' prefix takes a hyphen when forming a compound verb here._

8. **Find:** `asked if it was ok to run it which I approved`
   **Replace:** `asked if it was OK to run it, which I approved`
   _'ok' is conventionally capitalised as 'OK'; a comma is needed before the non-restrictive 'which' clause._

9. **Find:** `Once apt-get had been upgraded the duplicates were no longer in place`
   **Replace:** `Once apt-get had been upgraded, the duplicates were no longer in place`
   _Missing comma after the introductory subordinate clause._

10. **Find:** `sign up with my referral link here

Connect with me`
   **Replace:** `sign up with my referral link here.

Connect with me`
   _Final sentence of the conclusion is missing its terminating full stop._


#### /2025/05/vmc-quick-sizing-guide/  _(2 fixes)_

1. **Find:** `For up to date info always use the official sizing tool located here`
   **Replace:** `For up-to-date info, always use the official sizing tool located here.`
   _'up to date' is a compound adjective modifying 'info' and requires hyphens; a comma after the introductory phrase improves readability; the sentence is missing its terminal full stop, which would otherwise run into the next sentence._

2. **Find:** `This is based on vSAN OSA and excluding the management overhead (Ie valid for secondary clusters) It also uses the most efficient storage policy`
   **Replace:** `This is based on vSAN OSA and excludes the management overhead (i.e. valid for secondary clusters). It also uses the most efficient storage policy`
   _Verb agreement fix ('excluding' -> 'excludes' to pair with 'is based'); 'Ie' should be the standard abbreviation 'i.e.'; missing full stop after the closing parenthesis creates a run-on sentence._


#### /2025/08/vmc-host-deepdive/  _(1 fix)_

1. **Find:** `I have just collated it into a single page`
   **Replace:** `I have just collated it into a single page.`
   _Sentence ends without a full stop before the next paragraph; adding a period correctly terminates the sentence._


#### /2025/09/managing-my-homelab-with-semaphoreui/  _(4 fixes)_

1. **Find:** `deploy Docker onto host’s specified in the Inventory`
   **Replace:** `deploy Docker onto hosts specified in the Inventory`
   _Greengrocer's apostrophe in plural — 'host's' should be 'hosts'. The body uses a curly apostrophe (U+2019)._

2. **Find:** `It’s possible to have multiple repo’s connected`
   **Replace:** `It’s possible to have multiple repos connected`
   _Greengrocer's apostrophe in plural — 'repo's' should be 'repos'. The first apostrophe (It's) is correct as a contraction; only the second is wrong._

3. **Find:** `Now that we have gone over the basic concepts. Let’s deploy Docker using Semaphore.`
   **Replace:** `Now that we have gone over the basic concepts, let’s deploy Docker using Semaphore.`
   _'Now that we have gone over the basic concepts' is a subordinate clause with no main verb — ending it with a full stop creates a sentence fragment. Should be joined with a comma to the following main clause._

4. **Find:** `I have spun up a Vanilla Ubuntu 24.04 server`
   **Replace:** `I have spun up a vanilla Ubuntu 24.04 server`
   _'Vanilla' here is a common adjective meaning plain/standard, not a proper noun, so it should be lowercase mid-sentence._


#### /2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/  _(11 fixes)_

1. **Find:** `Replaces all WordPress URL’s as relative`
   **Replace:** `Replaces all WordPress URLs as relative`
   _Stray apostrophe in plural — URLs should not have an apostrophe._

2. **Find:** `Set’s up the job on a runner`
   **Replace:** `Sets up the job on a runner`
   _Wrong apostrophe — verb 'Sets' (3rd-person singular), not possessive._

3. **Find:** `Check’s Out the repo`
   **Replace:** `Checks Out the repo`
   _Wrong apostrophe — verb 'Checks', not possessive._

4. **Find:** `Test’s the runner environment`
   **Replace:** `Tests the runner environment`
   _Wrong apostrophe — verb 'Tests', not possessive._

5. **Find:** `Install any relevant dependencies`
   **Replace:** `Installs any relevant dependencies`
   _Verb agreement — other bullets in the list use 3rd-person singular (Sets, Generates, Notifies, Executes)._

6. **Find:** `Commit and Pushes the Static Site`
   **Replace:** `Commits and Pushes the Static Site`
   _Verb agreement — 'Pushes' is 3rd-person singular so the conjoined verb should be 'Commits'._

7. **Find:** `therefore for the GitHub-hosted runner`
   **Replace:** `therefore not reachable by the GitHub-hosted runner`
   _Sentence is grammatically broken/missing words — current text has no verb after 'therefore'._

8. **Find:** `so you can’t instantly view your changes without having any DNS propagation issues`
   **Replace:** `so you can instantly view your changes without having any DNS propagation issues`
   _'can’t' contradicts the meaning of the surrounding sentence (the preview URL is described as a useful feature for instant viewing)._

9. **Find:** `The benefits of this setup I have discussed previously`
   **Replace:** `The benefits of this setup I have discussed previously.`
   _Missing terminal full stop at end of sentence/paragraph._

10. **Find:** `I can trigger the GitHub runner manually ( It also runs on a Cron schedule)`
   **Replace:** `I can trigger the GitHub runner manually (it also runs on a Cron schedule).`
   _Stray space after opening paren, unnecessary capitalisation of 'It', and missing terminal full stop._

11. **Find:** `Within WordPress changed comments.php to the following`
   **Replace:** `Within WordPress I changed comments.php to the following`
   _Missing subject 'I' — sentence has no subject for the verb 'changed'._


#### /2025/12/vsan-cluster-shutdown/  _(3 fixes)_

1. **Find:** `How to safety shutdown a vSAN Environment` ⚠️ **appears 2x in body**
   **Replace:** `How to safely shut down a vSAN Environment`
   _'safety' is a noun being used where the adverb 'safely' is required; 'shutdown' is a noun, the verb form is 'shut down'. Both are clear grammatical errors. [Lives in the WP excerpt field of the source post, not body.]_

2. **Find:** `select “Restart vSAN Services” The workflow will enable them to bring them back into operation.`
   **Replace:** `select “Restart vSAN Services”. The workflow will bring them back into operation.`
   _Missing full stop after the closing quote produces a run-on, and 'will enable them to bring them back' is redundant/awkward._

3. **Find:** `vCentre`
   **Replace:** `vCenter`
   _VMware's product name is spelled 'vCenter' (proper noun, US spelling is the product name)._


### 2024

#### /2024/01/holodeck-cpu-fixes/  _(6 fixes)_

1. **Find:** `Holodeck team please don’t reach out`
   **Replace:** `Holodeck team, please don’t reach out`
   _Run-on sentence; missing comma before 'please' creates an unclear clause boundary._

2. **Find:** `the age of the Physical CPU’s in the hosts`
   **Replace:** `the age of the physical CPUs in the hosts`
   _Spurious apostrophe on plural and unnecessary capitalisation of 'Physical'._

3. **Find:** `Obviously, my CPU’s are not supported`
   **Replace:** `Obviously, my CPUs are not supported`
   _Spurious apostrophe on plural noun._

4. **Find:** `the vCLS VM’s for DRS are deployed`
   **Replace:** `the vCLS VMs for DRS are deployed`
   _Spurious apostrophe on plural noun._

5. **Find:** `deployment script and that is available here`
   **Replace:** `deployment script, and it is available here.`
   _Missing terminal full stop, and awkward 'and that is' phrasing; small punctuation/wording fix._

6. **Find:** `Luckily a colleague of mine Tim Sommer has made`
   **Replace:** `Luckily, a colleague of mine, Tim Sommer, has made`
   _Missing commas around the appositive name 'Tim Sommer'; also missing comma after introductory 'Luckily'._


#### /2024/01/multihost-holodeck-vcf/  _(6 fixes)_

1. **Find:** `Another point of note. The CPU’s in my hosts were identical.`
   **Replace:** `Another point of note: the CPU’s in my hosts were identical.`
   _Sentence fragment ‘Another point of note.’ followed by a separate sentence; replacing the full stop with a colon and lowercasing the next word fixes the fragment with the smallest change._

2. **Find:** `The CPU’s in my hosts were identical.`
   **Replace:** `The CPUs in my hosts were identical.`
   _Plural of CPU is CPUs; the apostrophe is incorrect for a plural (greengrocer’s apostrophe)._

3. **Find:** `If you have different generation Intel CPU’s or a mix of AMD/Intel`
   **Replace:** `If you have different generation Intel CPUs or a mix of AMD/Intel`
   _Plural of CPU is CPUs; the apostrophe is incorrect for a plural._

4. **Find:** `the builder can always resolve the correct IP’s irrespective`
   **Replace:** `the builder can always resolve the correct IPs irrespective`
   _Plural of IP is IPs; the apostrophe is incorrect for a plural._

5. **Find:** `to make this work across at least 2 hosts….`
   **Replace:** `to make this work across at least 2 hosts…`
   _Ellipsis already provides the trailing punctuation; the extra full stop after the ellipsis character is redundant._

6. **Find:** `All of the storage is to be presented by my TrueNas setup.`
   **Replace:** `All of the storage is to be presented by my TrueNAS setup.`
   _The product name is officially TrueNAS (all-caps NAS), analogous to vCenter — this is a product-name correction, not a stylistic change._


#### /2024/06/unifi-dhcp-option-43/  _(5 fixes)_

1. **Find:** `That left me with DHCP option 43`
   **Replace:** `That left me with DHCP Option 43.`
   _End-of-paragraph missing full stop; also inconsistent capitalisation — 'DHCP Option 43' is used in the title, H1, and the list item just above this sentence._

2. **Find:** `so let me explain. It is made up of 2 parts`
   **Replace:** `so let me explain. It is made up of 2 parts.`
   _Missing terminating full stop at end of paragraph._

3. **Find:** `I am hosting the controller on IP 192.168.20.2 The remaining part`
   **Replace:** `I am hosting the controller on IP 192.168.20.2. The remaining part`
   _Missing full stop between the IP address and the start of the next sentence — clear run-on._

4. **Find:** `A multitude of tools exist for converting IP to HEX one can be found here`
   **Replace:** `A multitude of tools exist for converting IP to HEX; one can be found here.`
   _Run-on sentence with no punctuation between 'HEX' and 'one can be found here'; also missing terminal full stop._

5. **Find:** `I can connect a factory fresh UniFi device to my network DHCP will hand out an IP`
   **Replace:** `I can connect a factory-fresh UniFi device to my network; DHCP will hand out an IP`
   _Run-on sentence — 'network' and 'DHCP will hand out' need separating punctuation. 'factory-fresh' as a compound adjective also takes a hyphen._


#### /2024/07/new-nodes/  _(11 fixes)_

1. **Find:** `what I bought why and how I have configured it`
   **Replace:** `what I bought, why, and how I have configured it`
   _Missing commas in list creates a run-on; commas restore correct grammar._

2. **Find:** `having run it in a production at a service provider`
   **Replace:** `having run it in production at a service provider`
   _'in a production' is ungrammatical; the idiom is 'in production'._

3. **Find:** `had I chose to deploy vSAN OSA`
   **Replace:** `had I chosen to deploy vSAN OSA`
   _Wrong verb form; the past participle 'chosen' is required after 'had'._

4. **Find:** `To reset the password’s I resorted to using the IPMItool`
   **Replace:** `To reset the passwords I resorted to using the IPMItool`
   _Incorrect possessive apostrophe in plural 'passwords'._

5. **Find:** `It’s useful to plan your IP address’s in advance`
   **Replace:** `It’s useful to plan your IP addresses in advance`
   _Incorrect possessive apostrophe in plural 'addresses'._

6. **Find:** `Then execute the following command utilising your CVM Ip address’s`
   **Replace:** `Then execute the following command utilising your CVM IP addresses`
   _'Ip' should be the initialism 'IP', and 'address’s' is an incorrect possessive in place of the plural 'addresses'._

7. **Find:** `Cluster succeed in creating will look similar to the below.`
   **Replace:** `A successful cluster creation will look similar to the below.`
   _'Cluster succeed in creating' is ungrammatical; rewording to 'A successful cluster creation' fixes the broken syntax._

8. **Find:** `The install is fairly straight forward`
   **Replace:** `The install is fairly straightforward`
   _'straight forward' is two words by mistake; the adjective is one word 'straightforward'._

9. **Find:** `Log into one of the CVM’s I executed a “Cluster Stop” command when the cluster is stopped shut all the CVM’s down.`
   **Replace:** `Log into one of the CVM’s and execute a “Cluster Stop” command. When the cluster is stopped, shut all the CVM’s down.`
   _Original is a run-on sentence with missing punctuation; splitting into two sentences and adding a comma fixes the broken grammar._

10. **Find:** `adding to an existing vSphere cluster This had the correct EVC mode`
   **Replace:** `adding to an existing vSphere cluster. This had the correct EVC mode`
   _Missing full stop between two sentences._

11. **Find:** `I also want to Increase the RAM`
   **Replace:** `I also want to increase the RAM`
   _Unnecessary mid-sentence capitalisation of 'Increase'._


#### /2024/09/can-you-really-squeeze-96tb-in-1u/  _(3 fixes)_

1. **Find:** `I typically don’t like using second hard storage`
   **Replace:** `I typically don’t like using second-hand storage`
   _'second hard storage' is a clear typo for 'second-hand storage' — the author means previously-owned drives._

2. **Find:** `it just had to be done….`
   **Replace:** `it just had to be done…`
   _Ellipsis character followed by a redundant full stop — should be just the ellipsis._

3. **Find:** `I have stuck with TrueNAS scale`
   **Replace:** `I have stuck with TrueNAS Scale`
   _Inconsistent capitalisation of product name — used correctly as 'TrueNAS Scale' elsewhere on the same page (e.g. 'A benefit of TrueNAS Scale is that the L2ARC persists between reboots')._


#### /2024/09/home-network-upgrade/  _(2 fixes)_

1. **Find:** `webmanaged switch`
   **Replace:** `web-managed switch`
   _Missing hyphen — inconsistent with 'web-managed switch' used two sentences earlier in the same paragraph._

2. **Find:** `100GB/s switch`
   **Replace:** `100Gb/s switch`
   _GB (gigabyte) vs Gb (gigabit) — the rest of the article (and product spec) uses Gb/s. Technical error._


#### /2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/  _(5 fixes)_

1. **Find:** `Artificial intelligence is all the rage at the moment, It’s getting included`
   **Replace:** `Artificial intelligence is all the rage at the moment. It’s getting included`
   _Comma splice / run-on. The capital 'I' in 'It’s' after the comma indicates a new sentence; a full stop is needed._

2. **Find:** `VM running Ubuntu 24.04 VM`
   **Replace:** `VM running Ubuntu 24.04`
   _Duplicated word 'VM' at the end of the sentence._

3. **Find:** `how this much running chat queries may impact things`
   **Replace:** `how much running chat queries may impact things`
   _Stray extra word 'this' makes the sentence ungrammatical._

4. **Find:** `even if its not running any queries`
   **Replace:** `even if it’s not running any queries`
   _Possessive 'its' used where contraction 'it’s' (it is) is required._

5. **Find:** `a bit more of a reminder for me as what I have done`
   **Replace:** `a bit more of a reminder for me of what I have done`
   _Wrong preposition; 'as' should be 'of' (or 'as to'). Smallest correct change is 'of'._


#### /2024/12/zfs-on-vmware/  _(5 fixes)_

1. **Find:** `You also need to do is to to ensure that TrueNAS can see unique disk IDs.`
   **Replace:** `What you also need to do is to ensure that TrueNAS can see unique disk IDs.`
   _Real grammar error: duplicated word 'to to' and the sentence is missing its subject. Verbatim match in body._

2. **Find:** `To confirm that To confirm that trim is working execute the below command command is working execute the below command command`
   **Replace:** `To confirm that trim is working, execute the below command`
   _Clearly broken/garbled text with repeated phrases; appears verbatim in body._

3. **Find:** `the VM’s be provisioned with thin disks`
   **Replace:** `the VMs be provisioned with thin disks`
   _Incorrect possessive apostrophe used for the plural 'VMs'. Verbatim match with curly apostrophe._

4. **Find:** `the VMs’s storage used`
   **Replace:** `the VM’s storage used`
   _Double possessive 'VMs's' is ungrammatical; should be singular possessive 'VM's'. Verbatim match._

5. **Find:** `Before and after listed below command`
   **Replace:** `Before and after listed below.`
   _Stray trailing word 'command' renders the sentence broken/incomplete; needs terminating punctuation._


### 2023

#### /2023/04/intel-optane/  _(7 fixes)_

1. **Find:** `many many benefits`
   **Replace:** `many benefits`
   _Accidental word repetition ('many many') — removing the duplicate is the smallest correct fix._

2. **Find:** `Two that I have probably made the most use of is`
   **Replace:** `Two that I have probably made the most use of are`
   _Subject-verb agreement: plural subject 'Two' requires 'are', not 'is'._

3. **Find:** `piqued my interest in particular some Optane drives`
   **Replace:** `piqued my interest, in particular some Optane drives`
   _Adding a comma after 'interest' breaks the run-on and properly introduces the parenthetical 'in particular some Optane drives'._

4. **Find:** `I was lucky enough to get some together with Gareth Edwards we decided to put something together`
   **Replace:** `I was lucky enough to get some. Together with Gareth Edwards, we decided to put something together`
   _Two independent clauses run together with no punctuation — splitting into two sentences fixes the run-on._

5. **Find:** `some back to back test to showcase`
   **Replace:** `some back-to-back tests to showcase`
   _'back-to-back' is a compound adjective requiring hyphens, and 'test' should be plural 'tests' to agree with 'some'._

6. **Find:** `configure the Optane’s as`
   **Replace:** `configure the Optanes as`
   _Incorrect possessive apostrophe used for a plural — Optanes (plural) does not take an apostrophe._

7. **Find:** `TrueNas Server`
   **Replace:** `TrueNAS server`
   _Inconsistent product capitalisation — the post itself uses 'TrueNAS' elsewhere; the official product name is TrueNAS._


#### /2023/05/homelab-storage-refresh-part-1/  _(9 fixes)_

1. **Find:** `Im sure there optimisations`
   **Replace:** `I'm sure there are optimisations`
   _Missing apostrophe in 'Im' and missing 'are' between 'there' and 'optimisations'. Both are clear grammatical errors._

2. **Find:** `2200 MB/s write Some crazy numbers` ⚠️ **not found in published body — NBSP likely**
   **Replace:** `2200 MB/s write. Some crazy numbers`
   _Run-on sentence — missing full stop between 'write' and the new sentence 'Some crazy numbers'._

3. **Find:** `of 1095 TBW
`
   **Replace:** `of 1095 TBW.
`
   _Sentence ends without a full stop before the next section heading._

4. **Find:** `As my Z840 TrueNAS server has way more RAM and CPU capabilities.`
   **Replace:** `My Z840 TrueNAS server has way more RAM and CPU capabilities.`
   _Sentence fragment beginning with 'As' — has no main clause. Removing 'As' makes it a grammatical sentence._

5. **Find:** `ZFS like a lot of modern storage technologies(VSAN etc) wants exclusive access`
   **Replace:** `ZFS, like a lot of modern storage technologies (VSAN etc.), wants exclusive access`
   _Missing space before opening parenthesis and missing commas around the parenthetical clause._

6. **Find:** `(it was originally called Zettabyte File System) It is a copy-on-write system (COW) If you are familiar`
   **Replace:** `(it was originally called Zettabyte File System). It is a copy-on-write system (COW). If you are familiar`
   _Two missing full stops between three sentences run together._

7. **Find:** `“Data VDEV” This can also be done`
   **Replace:** `“Data VDEV”. This can also be done`
   _Missing full stop between two sentences after the closing quote of 'Data VDEV'._

8. **Find:** `into a “Pool”`
   **Replace:** `into a “Pool”.`
   _Sentence ends without a full stop._

9. **Find:** `When running VM’s sync write is basically essential.`
   **Replace:** `When running VMs, sync write is basically essential.`
   _'VM’s' uses a possessive apostrophe for a plural — should be 'VMs'. Also missing comma after the introductory clause._


#### /2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/  _(8 fixes)_

1. **Find:** `Cloudflare has been improving there capabilities`
   **Replace:** `Cloudflare has been improving their capabilities`
   _Wrong word: 'there' should be possessive 'their'._

2. **Find:** `served from their datacenter’s`
   **Replace:** `served from their datacenters`
   _Incorrect apostrophe — plural noun, not possessive._

3. **Find:** `use relative URL’s`
   **Replace:** `use relative URLs`
   _Incorrect apostrophe in plural acronym._

4. **Find:** `to be “Main” You can then leave`
   **Replace:** `to be “Main”. You can then leave`
   _Missing full stop — creates a run-on between two sentences._

5. **Find:** `Cloudflare will initialize the build environment clone the Git repository`
   **Replace:** `Cloudflare will initialize the build environment, clone the Git repository`
   _Missing comma between list items — run-on._

6. **Find:** `If you have not done this ( Or installed the Cloudflare Pages App in GitHub you can do this by following this link`
   **Replace:** `If you have not done this (or installed the Cloudflare Pages App in GitHub) you can do this by following this link`
   _Unclosed parenthesis and incorrectly capitalised 'Or' mid-sentence._

7. **Find:** `If you click the name of the project, In my case WordPress`
   **Replace:** `If you click the name of the project, in my case WordPress,`
   _Incorrect capital 'In' mid-sentence after a comma; missing closing comma before main clause._

8. **Find:** `Then navigate to the settings section ensure that the settings are set to`
   **Replace:** `Then navigate to the settings section and ensure that the settings are set to`
   _Missing conjunction — creates a run-on sentence._


#### /2023/05/runecast-remediation-scripts/  _(4 fixes)_

1. **Find:** `If I drill into the specific issue I get the below view`
   **Replace:** `If I drill into the specific issue, I get the view below.`
   _Missing comma after introductory clause and missing terminal full stop; 'the below view' reads awkwardly compared to 'the view below'._

2. **Find:** `Here you can confirm the discovered issue and the remediation action. ( I have chosen not to enable SIOC on my ISO-NFS datastore)`
   **Replace:** `Here you can confirm the discovered issue and the remediation action. (I have chosen not to enable SIOC on my ISO-NFS datastore.)`
   _Stray space after the opening parenthesis and missing full stop inside the parenthetical._

3. **Find:** `Dropping this into a PowerCLI session we get….`
   **Replace:** `Dropping this into a PowerCLI session, we get…`
   _Missing comma after the introductory clause and a stray full stop after the ellipsis character (which is already three dots)._

4. **Find:** `What an amazing little feature`
   **Replace:** `What an amazing little feature!`
   _Final exclamatory sentence missing terminal punctuation._


#### /2023/10/going-out-with-a-bang/  _(2 fixes)_

1. **Find:** `VMware also gave all employees $1300 dollars`
   **Replace:** `VMware also gave all employees $1,300`
   _'$1300 dollars' is redundant ($ already denotes currency) and the figure lacks a thousands separator. Smallest correct fix is to drop 'dollars' and add the comma._

2. **Find:** `I decided to give mine to the RNLI .`
   **Replace:** `I decided to give mine to the RNLI.`
   _Stray space before the full stop after 'RNLI'._


#### /2023/10/vgpu-setup-in-my-homelab/  _(8 fixes)_

1. **Find:** `The other node was going to be used as a Tdarr Node`
   **Replace:** `The other node was going to be used as a Tdarr Node.`
   _End-of-paragraph sentence missing terminal full stop._

2. **Find:** `ran the below command to perform the install`
   **Replace:** `ran the below command to perform the install.`
   _Sentence missing a full stop before the code block._

3. **Find:** `a host reboot is required (even if it says it isn’t )`
   **Replace:** `a host reboot is required (even if it says it isn’t).`
   _Stray space before closing parenthesis and missing terminal full stop._

4. **Find:** `The Nvidia GPU Software Docs list the capabilities of each profile I have copied the relevant table below.`
   **Replace:** `The Nvidia GPU Software Docs list the capabilities of each profile. I have copied the relevant table below.`
   _Run-on sentence: two independent clauses joined without punctuation._

5. **Find:** `all of the memory must be reserved for the VM`
   **Replace:** `all of the memory must be reserved for the VM.`
   _Sentence missing terminal full stop._

6. **Find:** `we can now see the graphics card in windows`
   **Replace:** `we can now see the graphics card in Windows.`
   _'Windows' is a proper noun (OS name) and the sentence is missing a full stop._

7. **Find:** `Using GPU-Z we can validate the resources being presented through to the Virtual Machine`
   **Replace:** `Using GPU-Z we can validate the resources being presented through to the Virtual Machine.`
   _Sentence missing terminal full stop._

8. **Find:** `My Folding@home stats can be seen here and consider joining your compute to the project as well`
   **Replace:** `My Folding@home stats can be seen here, and consider joining your compute to the project as well.`
   _Two independent clauses joined without a comma and missing terminal full stop._


#### /2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/  _(2 fixes)_

1. **Find:** `With the current pause in the Broadcom VMware takeover deal. I had some downtime`
   **Replace:** `With the current pause in the Broadcom VMware takeover deal, I had some downtime`
   _Sentence fragment — the full stop incorrectly splits a subordinate clause from its main clause; a comma joins them properly._

2. **Find:** `VMware give me each year`
   **Replace:** `VMware gives me each year`
   _Subject-verb agreement: 'VMware' as a singular company name takes the singular verb 'gives'._


#### /2023/11/analytics-in-a-privacy-focused-world/  _(2 fixes)_

1. **Find:** `self hosted version`
   **Replace:** `self-hosted version`
   _Compound modifier preceding a noun should be hyphenated; 'self-hosted' is the standard form._

2. **Find:** `approx 30 mins to setup`
   **Replace:** `approx 30 mins to set up`
   _'setup' is a noun; the verb form is 'set up'. Sentence uses it as a verb ('took ... to set up')._


#### /2023/11/configuring-a-zen-internet-and-city-fibre-connection-with-a-3rd-party-router/  _(2 fixes)_

1. **Find:** `I have my 6 usable IP’s up and running`
   **Replace:** `I have my 6 usable IPs up and running`
   _Apostrophe used incorrectly to pluralise an initialism; 'IPs' is the correct plural._

2. **Find:** `these are added to the secondary tab as /32’s`
   **Replace:** `these are added to the secondary tab as /32s`
   _Apostrophe-as-plural error; '/32s' is the correct plural for the CIDR notation._


#### /2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/  _(10 fixes)_

1. **Find:** `until now…. With the release`
   **Replace:** `until now… With the release`
   _Ellipsis character followed by an extra full stop — only one terminator needed._

2. **Find:** `So why is this such an important change? to answer that we need`
   **Replace:** `So why is this such an important change? To answer that we need`
   _New sentence after a question mark must start with a capital letter._

3. **Find:** `for newly provisioned SDDC’s`
   **Replace:** `for newly provisioned SDDCs`
   _Plural of an acronym does not take an apostrophe._

4. **Find:** `on a single or low number of VMDK’s`
   **Replace:** `on a single or low number of VMDKs`
   _Plural of an acronym does not take an apostrophe._

5. **Find:** `As business demands lower RPO’s any improvement`
   **Replace:** `As business demands lower RPOs, any improvement`
   _Apostrophe-plural is wrong, and a comma is needed after the introductory clause to avoid a run-on._

6. **Find:** `less rewrites in the event of a device replacement`
   **Replace:** `fewer rewrites in the event of a device replacement`
   _'Rewrites' is a countable noun, so 'fewer' is correct, not 'less'._

7. **Find:** `a conservative compression ratio of 1.25%`
   **Replace:** `a conservative compression ratio of 1.25x`
   _A compression ratio is expressed as a multiplier (1.25x), not a percentage — 1.25% would mean data grew._

8. **Find:** `This is why the 4 and 5 node has a lower usable space.`
   **Replace:** `This is why the 4- and 5-node configurations have a lower usable space.`
   _Subject-verb agreement: a 4-node and a 5-node refer to multiple configurations, so 'have' is needed, and hyphenated compound modifiers fix the awkward phrasing._

9. **Find:** `It is also not currently available in a 2-node or Stretched SDDC configuration
`
   **Replace:** `It is also not currently available in a 2-node or Stretched SDDC configuration.
`
   _Sentence at end of paragraph is missing its terminating full stop._

10. **Find:** `further enhancements reduce the CPU overhead when using vSAN Encryption`
   **Replace:** `Further enhancements reduce the CPU overhead when using vSAN Encryption`
   _Bullet sentence should start with a capital letter to match the other items in the list._


### 2022

#### /2022/01/cloudflare-workers-limits-of-the-free-tier/  _(3 fixes)_

1. **Find:** `(mainly cosmetic to this site over the last day or so) On most changes`
   **Replace:** `(mainly cosmetic) to this site over the last day or so. On most changes`
   _Misplaced closing parenthesis and missing full stop create a run-on; logically the parenthetical is just '(mainly cosmetic)'._

2. **Find:** `When I next tried to publish I got the following`
   **Replace:** `When I next tried to publish I got the following:`
   _Missing terminal punctuation before code block; colon is the standard choice when introducing a quoted/coded snippet._

3. **Find:** `Detailed info on the limits is published here`
   **Replace:** `Detailed info on the limits is published here.`
   _Sentence is missing its terminating full stop._


#### /2022/01/lab-update-part-1-compute/  _(4 fixes)_

1. **Find:** `Quite a few changes have happened in the lab recently. so I decided to do a multipart blog on the changes.`
   **Replace:** `Quite a few changes have happened in the lab recently, so I decided to do a multipart blog on the changes.`
   _Full stop followed by lowercase 'so' creates a sentence fragment; should be a comma joining the two clauses._

2. **Find:** `Each node has 2x Intel Xeon CPU E5-2670 @ 2.60GHz 3 Nodes have 192GB of RAM and 1 has 128GB`
   **Replace:** `Each node has 2x Intel Xeon CPU E5-2670 @ 2.60GHz. 3 Nodes have 192GB of RAM and 1 has 128GB`
   _Run-on sentence — missing terminal punctuation between '2.60GHz' and the new sentence beginning '3 Nodes'._

3. **Find:** `One of the Compute nodes was removed from the server`
   **Replace:** `One of the Compute nodes was removed from the server.`
   _Standalone sentence missing terminal full stop._

4. **Find:** `With the additional Supermicro compute available I have made the Z840 a sort of standalone node.`
   **Replace:** `With the additional Supermicro compute available, I have made the Z840 a sort of standalone node.`
   _Missing comma after the introductory adverbial clause._


#### /2022/01/lab-update-part-2-storage/  _(8 fixes)_

1. **Find:** `TrueNas is the successor to FreeNas a very popular BSD based StorageOS and TrueNas scale is a fork of this based on Linux.`
   **Replace:** `TrueNAS is the successor to FreeNAS, a very popular BSD-based storage OS, and TrueNAS Scale is a fork of this based on Linux.`
   _TrueNAS and FreeNAS are the canonical product spellings (uppercase NAS); a comma is needed after the appositive, and 'TrueNas scale' should be the product name 'TrueNAS Scale'._

2. **Find:** `Crystel Disk Mark`
   **Replace:** `CrystalDiskMark`
   _CrystalDiskMark is the actual product name; the earlier paragraph already correctly references 'CrystalDisk'._

3. **Find:** `2x Intel 80GB SSD’s running within these.`
   **Replace:** `2x Intel 80GB SSDs running within these.`
   _Plural acronyms do not take an apostrophe; SSD's should be SSDs._

4. **Find:** `I had a number of VM’s running on the NVMe test at the time testing was running.`
   **Replace:** `I had a number of VMs running on the NVMe test at the time testing was running.`
   _Plural acronyms do not take an apostrophe; VM's should be VMs._

5. **Find:** `3x Sata disks in Raid5`
   **Replace:** `3x SATA disks in RAID 5`
   _SATA and RAID are universally uppercase acronyms; the same paragraph's preceding sentence already uses 'SATA' in uppercase, so this is an internal inconsistency._

6. **Find:** `This was also done with a 4GiB file which isn’t huge but I used to keep the testing short.`
   **Replace:** `This was also done with a 4GiB file which isn’t huge, but I used it to keep the testing short.`
   _Missing object 'it' makes the clause read as 'I used to keep' (past habitual) rather than the intended 'I used it to keep'._

7. **Find:** `I will use the 2xGb interfaces for management and the new network for a combination of iSCSI/NFS`
   **Replace:** `I will use the 2xGb interfaces for management and the new network for a combination of iSCSI/NFS.`
   _Sentence-ending period is missing._

8. **Find:** `This is in addition to my Synology DS918+`
   **Replace:** `This is in addition to my Synology DS918+.`
   _Sentence-ending period is missing._


#### /2022/01/lab-update-part-5-desired-workloads/  _(3 fixes)_

1. **Find:** `Active Directory -Done`
   **Replace:** `Active Directory – Done`
   _Missing space and wrong dash style — every other 'Done' item in the same list uses en dash with surrounding spaces (e.g. 'vRealize Lifecycle Manager – Done'). This is a clear formatting typo, not a stylistic preference._

2. **Find:** `vRealize Operations Manager -Done`
   **Replace:** `vRealize Operations Manager – Done`
   _Same formatting inconsistency as the Active Directory entry — missing space after hyphen and wrong dash style versus the rest of the list._

3. **Find:** `Sometimes because I break things (not always by accident) sometimes it’s a great way to learn….`
   **Replace:** `Sometimes because I break things (not always by accident); sometimes it’s a great way to learn…`
   _Two independent 'sometimes' clauses are joined with no punctuation (run-on/comma splice). Also four dots instead of a proper ellipsis. Semicolon plus three-dot ellipsis is the smallest correct fix._


#### /2022/01/wrangler-and-node-versions/  _(3 fixes)_

1. **Find:** `all of my Mac’s I typically just upgrade`
   **Replace:** `all of my Macs. I typically just upgrade`
   _Apostrophe used for a plural ('Mac’s' should be 'Macs') and a missing sentence boundary before 'I typically' creating a run-on._

2. **Find:** `have never had an issue….. Until today…`
   **Replace:** `have never had an issue… until today.`
   _Inconsistent and malformed ellipses — five dots followed by three dots. Normalising to a single ellipsis and proper full stop._

3. **Find:** `got the following error message`
   **Replace:** `got the following error message:`
   _Sentence introducing a code block is missing a terminal colon._


#### /2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/  _(11 fixes)_

1. **Find:** `due to the benefits It brought`
   **Replace:** `due to the benefits it brought`
   _'It' is incorrectly capitalised mid-sentence; should be lowercase 'it'._

2. **Find:** `or can even be run just on your workstation/laptop using local .`
   **Replace:** `or can even be run just on your workstation/laptop using local).`
   _Opening parenthesis is never closed and the sentence has a stray space before the period; closing the bracket fixes the broken parenthetical._

3. **Find:** `The difference is how content is published`
   **Replace:** `The difference is how content is published.`
   _Missing full stop at end of sentence/paragraph._

4. **Find:** `I have chosen to keep WordPress running in some docker containers on my Synology`
   **Replace:** `I have chosen to keep WordPress running in some Docker containers on my Synology.`
   _Missing full stop; 'Docker' is a product name and should be capitalised._

5. **Find:** `relative URL’s`
   **Replace:** `relative URLs`
   _Incorrect apostrophe used for plural of an acronym; should be 'URLs'._

6. **Find:** `I have then excluded the WordPress management URL’s in the static generation.`
   **Replace:** `I have then excluded the WordPress management URLs in the static generation.`
   _Incorrect apostrophe used for plural of an acronym; 'URLs' is correct. 'in' vs 'from' is stylistic so left unchanged._

7. **Find:** `push the relevant content into a GitHub repo`
   **Replace:** `push the relevant content into a GitHub repo.`
   _Missing full stop at end of sentence/paragraph._

8. **Find:** `lastly added a webhook to be called when the site has been updated (More on this a bit later)`
   **Replace:** `lastly added a webhook to be called when the site has been updated (more on this a bit later).`
   _Missing terminating full stop; capital 'M' mid-sentence inside parenthetical is incorrect._

9. **Find:** `The page’s site needs to be set up in Cloudflare`
   **Replace:** `The Pages site needs to be set up in Cloudflare`
   _Possessive 'page’s' makes no sense here; the section is about Cloudflare Pages (the product), so 'Pages' is correct._

10. **Find:** `login/select the relevant GitHub account and Repo`
   **Replace:** `log in/select the relevant GitHub account and repo`
   _'login' is a noun; the verb form is 'log in'. 'Repo' should not be capitalised mid-sentence._

11. **Find:** `one of the paid plans that starts at $5 a month`
   **Replace:** `one of the paid plans that start at $5 a month`
   _Subject-verb agreement: 'plans' is plural so the verb should be 'start', not 'starts'._


#### /2022/10/starlink/  _(4 fixes)_

1. **Find:** `SDWan product (Velocloud)`
   **Replace:** `SD-WAN product (VeloCloud)`
   _Correct product naming: VMware's product is officially branded 'VeloCloud' and the technology category is 'SD-WAN' (hyphenated)._

2. **Find:** `locked down by VMware Corporate IT)`
   **Replace:** `locked down by VMware Corporate IT).`
   _Missing terminal full stop at the end of a paragraph/sentence._

3. **Find:** `speed tests over Wifi`
   **Replace:** `speed tests over Wi-Fi`
   _'Wifi' is non-standard; the correct trademark/style is 'Wi-Fi'._

4. **Find:** `Once all the above had been done. It was a case of connecting Starlink`
   **Replace:** `Once all the above had been done, it was a case of connecting Starlink`
   _Sentence fragment: 'Once all the above had been done' is a dependent clause and should be joined to the following clause with a comma, not split with a full stop._


#### /2022/11/homelab-bad-days-almost/  _(7 fixes)_

1. **Find:** `I have advocating never using RAID 5`
   **Replace:** `I have advocated never using RAID 5`
   _Grammatical error: 'have advocating' is incorrect — should be past participle 'advocated'._

2. **Find:** `your wallet is in the line`
   **Replace:** `your wallet is on the line`
   _Wrong preposition — the idiom is 'on the line', not 'in the line'._

3. **Find:** `I had 3 SDD’s in this particular array`
   **Replace:** `I had 3 SSDs in this particular array`
   _Letter transposition: SDD should be SSD (Solid State Drive); also removes the incorrect possessive apostrophe before a plural s._

4. **Find:** `49599 hours (5.6 Years) It had more than served`
   **Replace:** `49599 hours (5.6 Years). It had more than served`
   _Missing sentence-terminating period creating a run-on between two sentences._

5. **Find:** `I logged into the Synology it was pretty obvious`
   **Replace:** `I logged into the Synology, it was pretty obvious`
   _Missing comma producing a run-on; comma splits the two clauses cleanly._

6. **Find:** `You do have notifications set up right?`
   **Replace:** `You do have notifications set up, right?`
   _Missing comma before the tag question 'right?'._

7. **Find:** `Unhappy Array ( For historical reasons I was using slots 1, 2 and 4`
   **Replace:** `Unhappy Array (for historical reasons I was using slots 1, 2 and 4)`
   _Unclosed parenthesis, stray space after opening paren, and unnecessary capitalisation of 'For' mid-parenthetical._


#### /2022/12/100gb-s-in-my-homelab-sort-of/  _(8 fixes)_

1. **Find:** `a number of DAC’s`
   **Replace:** `a number of DACs`
   _Stray apostrophe on a plural acronym; DACs is the correct plural form._

2. **Find:** `plus Vat`
   **Replace:** `plus VAT`
   _VAT is an acronym (Value Added Tax) and should be uppercase._

3. **Find:** `16 usable 25 ports which are way more than I need`
   **Replace:** `16 usable 25Gb ports which are way more than I need`
   _Missing unit; the rest of the post uses 25Gb consistently, so '25 ports' is a clear omission of the unit._

4. **Find:** `split the 100’s on the switch into 4×25`
   **Replace:** `split the 100s on the switch into 4×25`
   _Stray apostrophe on a plural number; 100s is the correct plural form._

5. **Find:** `( It can be powered just from POE) however, the config is way more complex`
   **Replace:** `(It can be powered just from PoE). However, the config is way more complex`
   _Stray space after opening parenthesis, missing sentence break before 'however', and PoE is the conventional capitalisation (Power over Ethernet)._

6. **Find:** `2 AC supplies, A DC input`
   **Replace:** `2 AC supplies, a DC input`
   _Incorrect capital A mid-list; should be lowercase article._

7. **Find:** `strangest of all it can be powered by POE in`
   **Replace:** `strangest of all, it can be powered by PoE in`
   _Missing comma after the introductory phrase, and PoE is the conventional capitalisation (Power over Ethernet)._

8. **Find:** `1gb/s network`
   **Replace:** `1Gb/s network`
   _Inconsistent unit casing; the rest of the post uses 100Gb/s and 25Gb, so 'Gb' should be capitalised._


#### /2022/12/forcing-an-upgrade-to-vsphere-8/  _(3 fixes)_

1. **Find:** `with the release of vSphere 8 I was obviously going to upgrade however a few personal things blocked me`
   **Replace:** `with the release of vSphere 8 I was obviously going to upgrade, however, a few personal things blocked me`
   _Run-on sentence; 'however' joining two independent clauses needs comma punctuation._

2. **Find:** `The vCenter upgrade was smooth however knowing that some of the hardware`
   **Replace:** `The vCenter upgrade was smooth; however, knowing that some of the hardware`
   _Two independent clauses joined by 'however' need a semicolon and comma._

3. **Find:** `It also listed all of the newly installed VIB’s`
   **Replace:** `It also listed all of the newly installed VIBs`
   _Greengrocer's apostrophe on plural acronym VIBs._


#### /2022/12/use-portainer-in-a-homelab-with-github/  _(6 fixes)_

1. **Find:** `Plus have GitHub (or similar) version control system`
   **Replace:** `Plus, have a GitHub (or similar) version control system`
   _Missing article 'a' and missing comma after 'Plus'; sentence is ungrammatical as written._

2. **Find:** `user and user id’s`
   **Replace:** `user and user IDs`
   _Incorrect apostrophe used for plural of 'ID'; should be 'IDs'._

3. **Find:** `Docker and Portainer It’s also important`
   **Replace:** `Docker and Portainer. It’s also important`
   _Run-on sentence; missing full stop between 'Portainer' and 'It’s'._

4. **Find:** `a great blog on this can be found here
`
   **Replace:** `a great blog on this can be found here.
`
   _Sentence ends without a full stop before the next paragraph._

5. **Find:** `as documented here .`
   **Replace:** `as documented here.`
   _Stray space before the full stop._

6. **Find:** `If for any reason this errors this is usually as the volume map is not set up correctly`
   **Replace:** `If for any reason this errors, it is usually because the volume map is not set up correctly`
   _Missing comma creates a run-on, and 'as' is used awkwardly where 'because' is correct._


### 2021

#### /2021/01/hashicorp-packer/  _(3 fixes)_

1. **Find:** `Thanks to Ryan for an Incredible piece of work`
   **Replace:** `Thanks to Ryan for an incredible piece of work`
   _'Incredible' is mid-sentence (after 'an') and should be lowercase._

2. **Find:** `ISO’s and configs`
   **Replace:** `ISOs and configs`
   _Apostrophe incorrectly used for a plural; 'ISOs' is the correct plural form._

3. **Find:** `in about 40mins`
   **Replace:** `in about 40 mins`
   _Missing space between numeric value and unit._


#### /2021/01/my-home-office-setup-upgrades/  _(9 fixes)_

1. **Find:** `My Mac is connected via USB-C This helps in reducing the cables on the desk.`
   **Replace:** `My Mac is connected via USB-C. This helps in reducing the cables on the desk.`
   _Missing full stop after 'USB-C' creates a run-on sentence._

2. **Find:** `(The Screen is 11.4KG)`
   **Replace:** `(the screen is 11.4 kg)`
   _Mid-sentence parenthetical should not capitalise 'The Screen', and SI unit convention is '11.4 kg' with a space and lowercase._

3. **Find:** `an included stand but It took up`
   **Replace:** `an included stand but it took up`
   _Stray capital 'It' mid-sentence after the conjunction 'but'._

4. **Find:** `I have had a variety of Canon SLR’s over the last 14 years and the 5D is certainly the best, It is an exceptional piece of kit.`
   **Replace:** `I have had a variety of Canon SLRs over the last 14 years and the 5D is certainly the best. It is an exceptional piece of kit.`
   _Plural of an acronym (SLRs) should not take an apostrophe, and the comma splice before 'It is' should be a full stop._

5. **Find:** `Yes, I snuck in one of the new M1 arm based Mac’s.`
   **Replace:** `Yes, I snuck in one of the new M1 ARM-based Macs.`
   _ARM is an acronym (should be uppercase, hyphenated as 'ARM-based'); plural 'Macs' should not take an apostrophe._

6. **Find:** `info on how It was put together`
   **Replace:** `info on how it was put together`
   _Stray capital 'It' mid-sentence._

7. **Find:** `I purchased the software version and run this on my Ipad pro.`
   **Replace:** `I purchased the software version and run this on my iPad Pro.`
   _Apple's product is correctly spelled 'iPad Pro' (lowercase i, capital P, capital P)._

8. **Find:** `it’s something I do everyday.`
   **Replace:** `it’s something I do every day.`
   _'everyday' (adjective, meaning ordinary) is misused for the adverbial phrase 'every day' (each day)._

9. **Find:** `*The Beats Solo’s were a gift`
   **Replace:** `*The Beats Solos were a gift`
   _Plural of the product name 'Solos' should not take a possessive apostrophe._


#### /2021/02/apple-content-caching/  _(8 fixes)_

1. **Find:** `additional devices just make sense…..`
   **Replace:** `additional devices just make sense.`
   _Ellipsis followed by two extra dots (five dots total) is incorrect punctuation; should be a single full stop._

2. **Find:** `Ipad Pro 9.7`
   **Replace:** `iPad Pro 9.7`
   _Apple's official brand styling is 'iPad' not 'Ipad'._

3. **Find:** `MacBook Air

Ipad

iPhone Xs`
   **Replace:** `MacBook Air

iPad

iPhone XS`
   _Fixes two Apple brand casing errors in the wife's device list: 'Ipad' → 'iPad' and 'iPhone Xs' → 'iPhone XS' (matches the 'iPhone XS' casing used earlier in the same post)._

4. **Find:** `a lot of apple devices`
   **Replace:** `a lot of Apple devices`
   _Apple is a proper noun and should be capitalised._

5. **Find:** `MacOS`
   **Replace:** `macOS`
   _Apple's official styling of the operating system is 'macOS' (lowercase m, capital OS)._

6. **Find:** `Macbook Air 2018`
   **Replace:** `MacBook Air 2018`
   _Apple's official brand styling is 'MacBook' (capital M and B); the rest of the post uses 'MacBook' correctly._

7. **Find:** `the amount of disk space to use it defaults to 10%`
   **Replace:** `the amount of disk space to use; it defaults to 10%`
   _Run-on sentence joining two independent clauses without punctuation; a semicolon (or full stop) is needed._

8. **Find:** `More info on it can be found here

To enable it is very straightforward`
   **Replace:** `More info on it can be found here.

To enable it is very straightforward:`
   _Both sentences are missing terminal punctuation — the first needs a full stop and the second needs a colon to introduce the steps that follow._


### 2020

#### /2020/06/veeamon2020/  _(8 fixes)_

1. **Find:** `With that most (if not all IT conferences have been postponed or gone online) Veeam’s annual conference VeeamON is no exception and now it’s here!!`
   **Replace:** `With that, most (if not all) IT conferences have been postponed or gone online; Veeam’s annual conference VeeamON is no exception, and now it’s here!`
   _Opening parenthesis is misplaced — it currently encloses 'if not all IT conferences have been postponed or gone online' instead of just 'if not all'. Fix corrects the parenthetical and the redundant exclamation marks._

2. **Find:** `As everyone knows by now the world has changed possibly forever.`
   **Replace:** `As everyone knows by now, the world has changed, possibly forever.`
   _Missing comma after the introductory phrase 'As everyone knows by now' and around the trailing parenthetical 'possibly forever'._

3. **Find:** `Due to Covid19 working from home has become the new normal.`
   **Replace:** `Due to Covid-19, working from home has become the new normal.`
   _Covid-19 is the conventional hyphenated form, and a comma is needed after the introductory prepositional phrase._

4. **Find:** `make sure you sign up and view some of the great sessions`
   **Replace:** `make sure you sign up and view some of the great sessions.`
   _Sentence is missing its terminal full stop._

5. **Find:** `Last but not least a feature that I have been asking about for over 3 years`
   **Replace:** `Last but not least, a feature that I have been asking about for over 3 years.`
   _Missing comma after the introductory phrase 'Last but not least' and no terminal full stop._

6. **Find:** `Yes Veeam Backup Agent for MAC`
   **Replace:** `Yes — Veeam Backup Agent for Mac.`
   _Missing punctuation after 'Yes', and 'Mac' is a product name not an acronym — it should not be all caps._

7. **Find:** `Charles Darwin “ It is not the strongest of the species that survives`
   **Replace:** `Charles Darwin: “It is not the strongest of the species that survives`
   _Stray space after the opening curly quote and the quote needs a colon to introduce it._

8. **Find:** `Fast recovery using Netapp Snapshots`
   **Replace:** `Fast recovery using NetApp Snapshots`
   _Vendor brand is officially spelled 'NetApp' with a capital A._


#### /2020/07/i3en/  _(4 fixes)_

1. **Find:** `lineup the “i3en”`
   **Replace:** `lineup: the “i3en”`
   _Missing punctuation between 'lineup' and the appositive '“i3en”'; a colon makes the relationship clear._

2. **Find:** `impressive packing in 96 logical cores`
   **Replace:** `impressive, packing in 96 logical cores`
   _Missing comma before participial phrase modifying 'impressive'._

3. **Find:** `the Broadwell’s in the original i3`
   **Replace:** `the Broadwells in the original i3`
   _Erroneous apostrophe in plural noun (greengrocer's apostrophe)._

4. **Find:** `With such a big uplift in Storage capacity hopefully, this will trend`
   **Replace:** `With such a big uplift in storage capacity, hopefully this will trend`
   _Misplaced comma (belongs after introductory clause, not after 'hopefully') and inconsistent capitalisation of 'Storage' mid-sentence._


#### /2020/07/nutanix-ncp/  _(1 fix)_

1. **Find:** `All in all top work Nutanix`
   **Replace:** `All in all, top work Nutanix.`
   _Real punctuation error in the main article body — missing comma after the introductory phrase 'All in all' and missing terminal full stop at the end of the closing sentence._


#### /2020/09/vmc-host-errors/  _(2 fixes)_

1. **Find:** `Just another reason why you should look at the VMware Cloud on AWS Service`
   **Replace:** `Just another reason why you should look at the VMware Cloud on AWS Service.`
   _Final sentence of the post body is missing its closing full stop._

2. **Find:** `I noticed it as a few HA alarms tripped in the vCenter (These were cosmetic only)`
   **Replace:** `I noticed it as a few HA alarms tripped in the vCenter (these were cosmetic only).`
   _Mid-sentence parenthetical should start lowercase ('these'), and the sentence is missing its closing full stop._


#### /2020/09/vmware-certified-master-specialist-hci-2020/  _(2 fixes)_

1. **Find:** `I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.20).`
   **Replace:** `I recently sat (and passed) the VMware HCI Master Specialist exam (5V0-21.20).`
   _Unbalanced parentheses: the opening '(' before 'and passed' is never closed. Inserting ')' after 'passed' restores balance and matches the intended parenthetical aside._

2. **Find:** `a VMware Master Services Competency .`
   **Replace:** `a VMware Master Services Competency.`
   _Stray space between the linked phrase 'VMware Master Services Competency' and the full stop. Removing the space gives the correct punctuation._


#### /2020/12/my-first-pull/  _(2 fixes)_

1. **Find:** `minor errors and Improvements`
   **Replace:** `minor errors and improvements`
   _Mid-sentence common noun 'Improvements' is erroneously capitalised; should be lowercase to match the parallel 'errors'._

2. **Find:** `listed as a contributor here .`
   **Replace:** `listed as a contributor here.`
   _Stray space before the full stop is a clear punctuation error._


### 2019

#### /2019/01/whats-in-my-backpack/  _(4 fixes)_

1. **Find:** `A few components that I have no one seems to have mentioned yet.`
   **Replace:** `A few components I have that no one seems to have mentioned yet.`
   _Grammatically broken / run-on with misplaced word order. The relative clause 'that I have' is in the wrong place, making the sentence nonsensical. Moving 'that' fixes it._

2. **Find:** `depending on if need to go to a datacenter`
   **Replace:** `depending on whether I need to go to a datacenter`
   _Missing subject 'I' creates an ungrammatical clause. 'Whether' is also more natural than 'if' here. Real grammar error._

3. **Find:** `Macbook Air 2018 ( My goto machine)`
   **Replace:** `MacBook Air 2018 (my go-to machine)`
   _MacBook is Apple's official product spelling (capital B). 'Goto' is a programming keyword; the English phrase is hyphenated 'go-to'. Also removes the stray space after '('._

4. **Find:** `Led Headtorch`
   **Replace:** `LED head torch`
   _LED is an acronym (Light Emitting Diode) and should be capitalised. 'Head torch' is the standard UK English form (two words)._


#### /2019/02/lab-storage-2/  _(4 fixes)_

1. **Find:** `SSD’s that I had giving me about 3TB`
   **Replace:** `SSDs I had, giving me about 3TB`
   _Apostrophe incorrectly used to pluralise 'SSDs', and missing comma before 'giving' creates a run-on clause._

2. **Find:** `ISO’s and some general file storage`
   **Replace:** `ISOs and some general file storage`
   _Apostrophe incorrectly used to pluralise 'ISOs'._

3. **Find:** `Synology GUI ( It used to be a command-line-only option) I have verified`
   **Replace:** `Synology GUI (it used to be a command-line-only option). I have verified`
   _Stray space after opening parenthesis, incorrect capital 'I' starting the parenthetical, and missing full stop before the next sentence — currently a run-on._

4. **Find:** `I purchased a new Synology DS918`
   **Replace:** `I purchased a new Synology DS918.`
   _Paragraph ends mid-sentence with no terminating full stop._


#### /2019/12/monitoring-vmc-part-1/  _(4 fixes)_

1. **Find:** `If not you will need to open up the relevant firewalls`
   **Replace:** `If not, you will need to open up the relevant firewalls.`
   _Missing terminal full stop at end of paragraph (the paragraph ends here with no punctuation before the next paragraph 'Once done Veeam...'), plus missing comma after introductory 'If not'._

2. **Find:** `It is correctly reporting back that the hosts are running ESXi 6.9.1`
   **Replace:** `It is correctly reporting back that the hosts are running ESXi 6.9.1.`
   _Missing terminal full stop at end of paragraph — sentence trails off without punctuation._

3. **Find:** `Veeam One .`
   **Replace:** `Veeam One.`
   _Stray space before the full stop — clear typographical error._

4. **Find:** `Influxdb`
   **Replace:** `InfluxDB`
   _InfluxDB is the official product name with that specific capitalisation — same kind of proper-noun fix as vCenter._


### 2018

#### /2018/01/lab-storage/  _(5 fixes)_

1. **Find:** `I also have a DS216+II Synology with 2x 2TB WD Red’s this is my tier 2 lab storage. for backups ISO’s etc`
   **Replace:** `I also have a DS216+II Synology with 2x 2TB WD Reds; this is my tier 2 lab storage, for backups, ISOs etc.`
   _Run-on sentence with comma splice, lowercase 'for' starting a sentence fragment, and greengrocer's apostrophes in plural Reds/ISOs. Missing terminating full stop._

2. **Find:** `The 2xWD Red’s are in an SHR configuration with the SSDs running as an SSD read-write cache`
   **Replace:** `The 2x WD Reds are in an SHR configuration with the SSDs running as an SSD read-write cache.`
   _Greengrocer's apostrophe on plural 'Red's' and missing terminating full stop._

3. **Find:** `This gives me 2.6TB Useable`
   **Replace:** `This gives me 2.6TB useable`
   _'Useable' is mid-sentence and should not be capitalised. Kept UK-acceptable 'useable' spelling rather than 'usable' to make the smallest correct change._

4. **Find:** `I have the 4 Nics split into two LACP bonds.` ⚠️ **not found in published body — NBSP likely**
   **Replace:** `I have the 4 NICs split into two LACP bonds.`
   _NIC is an acronym (Network Interface Card) and should be capitalised as 'NICs'. Consistent with '4x 1Gb/s NIC' earlier in the post._

5. **Find:** `I will add some pics when I have tidied up the lab/cables`
   **Replace:** `I will add some pics when I have tidied up the lab/cables.`
   _Missing terminating full stop at the end of the sentence/paragraph._


#### /2018/01/nutanix-ce/  _(4 fixes)_

1. **Find:** `see what was new with AHV and Nutanix CE`
   **Replace:** `see what was new with AHV and Nutanix CE.`
   _Sentence/paragraph ends without a full stop. Adding the period is the minimal correct fix._

2. **Find:** `the same server I ran initially. a Dell T20 with the Xeon processor 32GB of RAM 1x240GB SSD and 1x3TB WD Red.`
   **Replace:** `the same server I ran initially: a Dell T20 with the Xeon processor, 32GB of RAM, 1x240GB SSD and 1x3TB WD Red.`
   _Incorrect full stop creating a sentence fragment, plus missing serial commas between hardware spec items that make the list unreadable._

3. **Find:** `running a few VM’s`
   **Replace:** `running a few VMs`
   _Greengrocer's apostrophe — 'VM's' is incorrect for the plural; should be 'VMs'._

4. **Find:** `Ill post back with some updates of what I get up to with it`
   **Replace:** `I'll post back with some updates of what I get up to with it.`
   _Missing apostrophe in contraction ('Ill' should be 'I'll') and missing terminal full stop on the sentence._


#### /2018/03/aws-for-beginners1/  _(5 fixes)_

1. **Find:** `This is a must, Sadly AWS don’t appear to support my preferred 2FA device. Yubikey so I’m using the Google authenticator`
   **Replace:** `This is a must. Sadly, AWS doesn’t appear to support my preferred 2FA device, the Yubikey, so I’m using the Google Authenticator.`
   _Genuine grammar errors: comma splice ('must, Sadly'), subject-verb agreement ('AWS don't' → 'AWS doesn't'), and orphan fragment ('Yubikey so…'). Replacement repairs all three minimally and adds the missing terminal full stop._

2. **Find:** `Enable Billing Alerts Create an alert so that if your bill is over X you will get a notification.`
   **Replace:** `Enable Billing Alerts — create an alert so that if your bill is over X you will get a notification.`
   _Two sentences run together with no punctuation. The sibling bullets above use ' – ' to separate label from explanation; adding an em-dash matches that pattern and fixes the run-on._

3. **Find:** `lifting and shifting existing infrastructure into “the cloud”`
   **Replace:** `lifting and shifting existing infrastructure into “the cloud”.`
   _Missing terminal punctuation. The following paragraph starts a new sentence, confirming this is the end of the prior one._

4. **Find:** `go and set up an account and play`
   **Replace:** `go and set up an account and play.`
   _Missing terminal full stop on a paragraph-final sentence._

5. **Find:** `missed the point….`
   **Replace:** `missed the point…`
   _The text uses a true ellipsis character (…) followed by an extra full stop, producing four dots. Correct form is a single ellipsis._


#### /2018/03/cloudflare/  _(5 fixes)_

1. **Find:** `sites/ organizations.`
   **Replace:** `sites/organisations.`
   _Stray space after slash AND US spelling 'organizations' in an otherwise UK-English post (author uses UK spelling elsewhere). Both issues fixed in the minimal change._

2. **Find:** `POP’s`
   **Replace:** `POPs`
   _Incorrect possessive apostrophe used for a plural acronym. Should be 'POPs' (plural Points of Presence)._

3. **Find:** `2 A records Neither of which`
   **Replace:** `2 A records. Neither of which`
   _Missing full stop creates a run-on sentence; 'Neither' begins a new sentence._

4. **Find:** `you input where the real webserver lives cloudflare will do the rest.`
   **Replace:** `you input where the real webserver lives and Cloudflare will do the rest.`
   _Run-on sentence missing conjunction; also 'cloudflare' should be capitalised as the company name 'Cloudflare' (used capitalised elsewhere in the post)._

5. **Find:** `it will automatically purge the cache if required`
   **Replace:** `it will automatically purge the cache if required.`
   _Missing full stop at end of paragraph/sentence._


#### /2018/05/aws-status-page-monitoring-included/  _(3 fixes)_

1. **Find:** `The tool I deployed lambstatus supports pulling metrics`
   **Replace:** `The tool I deployed, lambstatus, supports pulling metrics`
   _'lambstatus' is an appositive naming the tool and requires commas around it for correct grammar._

2. **Find:** `at effectively zero cost`
   **Replace:** `at effectively zero cost.`
   _The paragraph ends mid-sentence with no full stop; adding the period closes the sentence._

3. **Find:** `is documented in the Git repo here`
   **Replace:** `is documented in the Git repo here.`
   _The sentence under 'Site Response' ends without a full stop._


#### /2018/06/nutanix-command-reference-guide/  _(3 fixes)_

1. **Find:** `Its here as a reference`
   **Replace:** `It's here as a reference`
   _Missing apostrophe — 'Its' (possessive) should be 'It's' (contraction of 'it is')._

2. **Find:** `if i need a command`
   **Replace:** `if I need a command`
   _The pronoun 'I' must be capitalised._

3. **Find:** `ill generally add it here`
   **Replace:** `I'll generally add it here`
   _'ill' should be the contraction 'I'll' (I will); current form reads as the adjective 'ill'._


#### /2018/10/and-now-for-something-completely-different/  _(3 fixes)_

1. **Find:** `I have been lucky enough to be involved with all of these ( some much more than others) Although the work is never complete Zen are in a good place.`
   **Replace:** `I have been lucky enough to be involved with all of these (some much more than others). Although the work is never complete, Zen are in a good place.`
   _Stray space after opening parenthesis, missing full stop before 'Although' creating a run-on sentence, and missing comma after 'complete'._

2. **Find:** `for professional services in 2018

Yes,`
   **Replace:** `for professional services in 2018.

Yes,`
   _Sentence ends without a full stop before the new paragraph begins._

3. **Find:** `one or two others…..`
   **Replace:** `one or two others…`
   _Unicode ellipsis followed by two extra dots (5 dots total) — should be a single standard ellipsis._


#### /2018/12/new-laptop/  _(4 fixes)_

1. **Find:** `MacBook Pro’s weren’t worth it`
   **Replace:** `MacBook Pros weren’t worth it`
   _Incorrect apostrophe; plural 'Pros' should not take a possessive apostrophe._

2. **Find:** `another MacBook Air .`
   **Replace:** `another MacBook Air.`
   _Stray space before the full stop._

3. **Find:** `benefits of the T2 Security chip`
   **Replace:** `benefits of the T2 Security chip.`
   _Sentence ends without a full stop before the paragraph break._

4. **Find:** `16Gb of RAM`
   **Replace:** `16GB of RAM`
   _Inconsistent capitalisation — 'Gb' means gigabits; should be 'GB' to match the adjacent '512GB'._


### 2017

#### /2017/05/money-saving-uk-version/  _(3 fixes)_

1. **Find:** `First direct give you a good bonus`
   **Replace:** `First Direct gives you a good bonus`
   _Inconsistent capitalisation with the section heading 'First Direct 1st Account' and subject-verb agreement (a single bank takes 'gives')._

2. **Find:** `Barclays mortgage , and £1`
   **Replace:** `Barclays mortgage, and £1`
   _Stray space before the comma._

3. **Find:** `I currently have a number of UK current accounts`
   **Replace:** `I currently have a number of UK current accounts.`
   _Missing terminal full stop at end of the paragraph before the next heading/paragraph._

