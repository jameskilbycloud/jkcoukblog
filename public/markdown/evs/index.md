---
title: "Amazon Elastic VMware Service (AWS EVS) – Links & Resources"
description: "A curated collection of links and resources for Amazon Elastic VMware Service (AWS EVS) — official docs, design guides, pricing, networking, HCX, and the latest announcements from Broadcom and AWS."
date: 2025-06-18T11:21:48+00:00
modified: 2026-07-23T21:17:22+00:00
author: James Kilby
url: https://jameskilby.co.uk/evs/
image: https://jameskilby.co.uk/wp-content/uploads/2026/02/maxresdefault.jpg
---

# Amazon Elastic VMware Service (AWS EVS) – Links & Resources

My role at Broadcom is to look after VMware-based AWS HyperScaler Solutions — including VMware Cloud on AWS (VMC) and Amazon Elastic VMware Service (AWS EVS). This page is a curated, regularly updated collection of shortcuts to the public-facing EVS documentation on Broadcom and AWS’s websites, covering design, pricing, networking, operations, HCX, workloads, and the latest service announcements.

## Table of Contents

## Service Status

[AWS Service Status Dashboard](https://health.aws.amazon.com/health/status)

## Service Announcement

[Announcement](https://aws.amazon.com/blogs/migration-and-modernization/whats-next-for-vmware-workloads-on-aws/)

[Amazon Elastic VMware Service: Start your modernization journey](https://www.youtube.com/watch?v=OJ7cR7HxUPs)

[New Regions ](https://aws.amazon.com/about-aws/whats-new/2025/12/amazon-evs-available-in-additional-regions/)

[32 Host Limit](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-evs-32-hosts/)

[VCF 9.0 & 9.1 Support](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-evs-vcf9/)

[VCF & ESX Version Selection](https://aws.amazon.com/about-aws/whats-new/2026/01/amazon-evs-vcf-vmware-esx-software-version)

[Document History (What’s New)](https://docs.aws.amazon.com/evs/latest/userguide/doc-history.html)

## Reinvent Media

### 2025

[A complete guide to Amazon EVS: Unlock AWS scale for VMware workloads (MAM201)](https://www.youtube.com/watch?v=d0TLechcV74)

[Optimizing storage costs for Amazon EVS with FSx for ONTAP (MAM101)](https://www.youtube.com/watch?v=vFlKJX7DEj0)

### 2024

[Amazon Elastic VMware Service: Start your modernization journey with AWS (MAM119](https://www.youtube.com/watch?v=OJ7cR7HxUPs))

## Design

[User Guide PDF](https://docs.aws.amazon.com/pdfs/evs/latest/userguide/evs-ug.pdf)

[NSX Edge Cluster Deployment – For Operations Automation and Logs](https://aws.amazon.com/blogs/migration-and-modernization/enhancing-amazon-elastic-vmware-service-deploying-the-nsx-edge-cluster-through-sddc-manager-for-application-virtual-networks/)

[NSX Multi EDGE ](https://aws.amazon.com/about-aws/whats-new/2026/01/amazon-evs-multiple-vmware-nsx-edge-gateways/)

[API Reference Guide](https://docs.aws.amazon.com/pdfs/evs/latest/APIReference/evs-api.pdf)

[AWS CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/evs/)

[Automated Deployment ](https://github.com/aws-solutions-library-samples/guidance-for-automated-setup-for-elastic-vmware-service-on-aws)

[Cloudformation](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/AWS_EVS.html)

[Deployment Checklist](https://docs.aws.amazon.com/evs/latest/userguide/evs-deployment-prereq-checklist.html)

[Licensing](https://www.vmware.com/docs/vmware-cloud-foundation-license-portability-list-of-certified-cloud-providers)

[Trial Licensing ](https://knowledge.broadcom.com/external/article/263840/broadcom-trial-software-and-proof-of-con.html)

[Documentation Home](https://docs.aws.amazon.com/evs/)

[Getting Started](https://docs.aws.amazon.com/evs/latest/userguide/getting-started.html)

## Management Sizing

A few people have asked me what the management stack in VCF looks like and how much resource is consumed. Here are the specs of the virtual machines that get deployed in the current version

**Component**| **vCPU**| **Memory (GB)**| **Disk (Gib)**  
---|---|---|---  
vCentre| 8| 30| 916  
SDDC Manager| 4| 16| 909  
NSX Manager| 6| 24| 300  
NSX Manager| 6| 24| 300  
NSX Manager| 6| 24| 300  
NSX Edge| 4| 8| 197  
NSX Edge| 4| 8| 197  
**Total**|  38| 134| 3118  
  
[Setting Up (Prerequisites & Hosts)](https://docs.aws.amazon.com/evs/latest/userguide/setting-up.html)

## Operations

[Environment Lifecycle Management](https://docs.aws.amazon.com/evs/latest/userguide/evs-lifecycle-mgmt.html)

[AI-Powered Operational Monitoring (Digital Twin)](https://github.com/aws-solutions-library-samples/guidance-for-ev-digital-twin-ai-powered-operational-monitoring)

## Networking

[EVS Architecture (VPC, VLAN Subnets, Route Server, NSX)](https://docs.aws.amazon.com/evs/latest/userguide/architecture.html)

## Monitoring

[Monitor EVS VPCs with Amazon CloudWatch](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cloudwatch.html)

## Security

[Identity & Access Management (IAM)](https://docs.aws.amazon.com/evs/latest/userguide/security-iam.html)

[IAM Identity-Based Policy Examples](https://docs.aws.amazon.com/evs/latest/userguide/security-iam-id-based-policy-examples.html)

[Data Protection & Encryption](https://docs.aws.amazon.com/evs/latest/userguide/data-protection.html)

[Secure EVS with AWS Network Firewall](https://aws.amazon.com/blogs/architecture/secure-amazon-elastic-vmware-service-amazon-evs-with-aws-network-firewall/)

## Pricing

[Price Calculator](https://aws.amazon.com/evs/pricing/)

## External Storage

[NetApp ONTAP](https://docs.aws.amazon.com/evs/latest/userguide/fsx-ontap.html)

## Performance

## Walkthrough

[Interactive Walkthrough 1](https://amazon.storylane.io/share/xtislcaqnanc)

[Interactive Walkthrough 2](https://amazon.storylane.io/share/jvwyquiubg3k)

## HCX

[Migration](https://docs.aws.amazon.com/evs/latest/userguide/migrate-evs-hcx.html)

[Migrating from VMware Cloud on AWS to EVS](https://repost.aws/articles/ARo3N3YBmQR0WcL1SOya6GfQ/migration-from-vmware-cloud-on-aws-to-amazon-evs-with-fsx-for-ontap)

## Workloads

[Oracle Database on EVS + FSx for ONTAP: Best Practices](https://repost.aws/articles/AR3bnQsABSSIS0J8pO8mIUCA/oracle-database-deployment-on-amazon-evs-and-fsx-for-netapp-ontap-best-practices)

## IAC

[Automated Setup for Amazon EVS (AWS Solution)](https://docs.aws.amazon.com/solutions/automated-setup-for-amazon-elastic-vmware-service/)

[Solutions for EVS (GitHub)](https://github.com/aws-solutions-library-samples/guidance-for-automated-setup-for-elastic-vmware-service-on-aws)

[Deploying VCF 9.1 on EVS: End-to-End Automation](https://aws.amazon.com/blogs/migration-and-modernization/deploying-vcf-9-1-on-amazon-evs-with-end-to-end-automation/)

[Deploy FSx for ONTAP with Terraform](https://aws.amazon.com/blogs/storage/deploying-amazon-fsx-for-netapp-ontap-hashicorp-terraform/)

## Useful Blogs

[vcloudone.com](http://vcloudone.com)

[Deploying VCF 9.1 on Amazon EVS with End-to-End Automation](https://aws.amazon.com/blogs/migration-and-modernization/deploying-vcf-9-1-on-amazon-evs-with-end-to-end-automation/)