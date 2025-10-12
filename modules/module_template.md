# Terraform AWS {{MODULE_SHORT_NAME}} Module

## Module Information

<!-- TEMPLATE INSTRUCTIONS:
Extract module metadata and create standardized module information section.

Generate the following bullet points in order:

1. **Module Name**:
 - Format: - **Module Name**: `{short-module-name}`
 - Extract short name from full module path (e.g., `terraform-aws-modules/vpc/aws` → `vpc`)
 - Example: `vpc`, `s3-bucket`, `security-group`

2. **Source**:
 - Format: - **Source**: `{terraform-module-source-path}`
 - Extract from module source or registry
 - Example: `terraform-aws-modules/vpc/aws`

3. **GitHub Repository**:
 - Format: - **GitHub Repository**: {full-github-url}
 - Construct from source path or find in documentation
 - Example: https://github.com/terraform-aws-modules/terraform-aws-vpc

4. **Terraform Registry**:
 - Format: - **Terraform Registry**: {registry-url}
 - Standard format: https://registry.terraform.io/modules/{namespace}/{module}/{provider}/latest
 - Example: https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest

5. **Latest Version**:
 - Format: - **Latest Version**: {version-number OR "Check registry for current version"}
 - Include actual version if available, otherwise use placeholder text
 - Version can be found on registry module web-page in block "Provision Instructions"
 - Alternatively, try to find on Github releases page
 - Example: 5.0.0, 3.2.1, Check registry

6. **Purpose**:
 - Format: - **Purpose**: {One-sentence description of what the module creates/manages}
 - Extract from module README or description
 - Focus on primary resources created (e.g., "Terraform module that creates AWS VPC resources")

7. **Service**:
 - Format: - **Service**: {AWS Service Name (Full Name)}
 - Example: AWS VPC (Virtual Private Cloud), AWS S3 (Simple Storage Service)
 - Use official AWS service names

8. **Category**:
 - Format: - **Category**: {Primary category, Secondary category}
 - Common categories: Networking, Storage, Compute, Database, Security, Monitoring, Analytics, etc.
 - List 1-3 relevant categories separated by commas

9. **Keywords**:
 - Format: - **Keywords**: {comma-separated-keyword-list}
 - Extract from module tags, README, or infer from functionality
 - Include: resource types, features, use cases, abbreviations, related services
 - 20-50 keywords covering technical terms, features, integrations, and use cases
 - Examples: vpc, subnet, nat-gateway, internet-gateway, route-table, security-group

10. **Use For**:
 - Format: - **Use For**: {comma-separated list of practical use cases}
 - 8-12 practical, real-world scenarios where this module would be used
 - Focus on business/technical outcomes, not technical features
 - Example: multi-tier application hosting, microservices networking, hybrid cloud connectivity
-->

## Description

<!-- TEMPLATE INSTRUCTIONS:
Analyze the source module documentation and generate a clear, comprehensive description.

Instructions:
1. Read and extract information from:
 - Module README files
 - Official documentation
 - Module repository descriptions
 - Provider documentation (AWS, Azure, GCP, etc.)

2. Structure the description in 2-3 paragraphs covering:
 - What the module does (resources it creates/manages)
 - Why it exists (problems it solves)
 - Key capabilities and features
 - Architectural approach (if applicable)
 - Integration points (if relevant)

3. Writing guidelines:
 - Summarize in your own words, do not copy-paste
 - Use clear, technical language (third person)
 - Focus on WHAT and WHY, not HOW
 - Include specific resource types managed by the module
 - Mention any submodules or architectural patterns
 - Reference the underlying service/platform being managed
 - 150-300 words total

4. Content priorities:
 - Primary: Module purpose and resources
 - Secondary: Service/platform overview
 - Tertiary: Unique features, compliance, security aspects

If documentation is sparse, infer from:
- Module source code structure
- Resource definitions
- Example configurations
- Provider registry information

Output format: 2-3 well-structured paragraphs of descriptive text (no bullets or lists).
-->

## Key Features

<!-- TEMPLATE INSTRUCTIONS:
Extract and organize key features from the module documentation into a bulleted list.

Feature extraction guidelines:
1. Analyze documentation to identify:
 - Submodules/components available
 - Core capabilities and functionality
 - Integration points with other services
 - Configuration options and flexibility
 - Security features (encryption, IAM, policies)
 - Non-functional features (tagging, cross-region, monitoring)
 - Compliance and standards support
 - Management and operational features

2. Structure each feature bullet point:
 - Format: - **{Feature Name/Title}**: {Brief description}
 - Bold the feature name or key term
 - Follow with colon and concise description (5-15 words)
 - Use active, descriptive language
 - Focus on capabilities, not implementation details

3. Feature categories to include (if applicable):
 - Components/Submodules (list major ones)
 - Core functionality (what it creates/manages)
 - Advanced features (special capabilities)
 - Integration options (AWS services, third-party)
 - Security & Compliance (encryption, policies, standards)
 - Configuration (flexibility, customization)
 - Operational (tagging, monitoring, logging)
 - Performance (optimization, scaling)

4. Organization approach:
 - Start with most important/distinctive features
 - Group related features together
 - List 10-25 features depending on module complexity
 - Balance between specificity and brevity

5. Writing style:
 - Use parallel structure (consistent verb forms)
 - Be specific (mention actual services/features by name)
 - Avoid vague terms like "various options" or "multiple features"
 - Include technical terms and AWS service names
 - Quantify when possible (e.g., "13 Specialized Submodules")

Example patterns:
- **{Component Name}**: {What it does}
- **{Feature Name}**: {Capability or benefit}
- **{Integration Type}**: {Integration description}
- **{Configuration Aspect}**: {Flexibility or customization available}

Output: 10-25 bulleted items with bold titles and descriptions.
-->

## Main Use Cases

<!-- Generate 8-10 use cases covering these categories:
- Monitoring (infrastructure, applications, performance)
- Security & Compliance (detection, auditing, controls)
- Operations (logging, alerting, incident response)
- Optimization (cost, capacity, performance tuning)
- Analytics (real-time processing, anomaly detection, trends)

Format: {number}. **{Title}**: {Description (5-10 words)}
-->

## Submodules

<!-- SUBMODULES TEMPLATE:
Generate a numbered list of submodules. For each submodule:
1. Create heading: ### {number}. {submodule-name}
2. Include exactly 4 bullet points:
 - **Purpose**: One-line description of what it creates
 - **Source**: Full Terraform module source path
 - **Documentation Link**: Direct link to submodule documentation on registry.terraform.io (example: https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest/submodules/vault)
 - **Key Features**: Comma-separated list of 2-4 key capabilities
 - **Use Cases**: Comma-separated list of 2-4 practical use cases
-->

<!-- TEMPLATE INSTRUCTIONS:
For each submodule in the source module, create a detailed documentation section.

Structure for each submodule:

### Submodule Heading:
- Format: ## Submodule {number}: {submodule-name}
- Number sequentially starting from 1
- Use exact submodule name from source documentation

### Required Subsections (in order):

1. **Description** (### Description):
 - 1-3 sentence overview of what the submodule does
 - Focus on primary purpose and resources created
 - Mention key differentiators from other submodules

2. **Key Features** (### Key Features):
 - Bulleted list of 3-7 key capabilities
 - Each bullet is a concise feature description
 - Focus on what the submodule enables or provides
 - Use active language (e.g., "Password complexity requirements")

3. **Input Variables** (### Input Variables):
 - Markdown table with columns: Variable | Type | Default | Description
 - Extract from module variables.tf or documentation
 - Include only important/commonly-used variables
 - Use code formatting for values: `string`, `true`, `""`
 - Keep descriptions concise (one line)
 - Order: required variables first, then optional by importance
 - Don't create subsections for required/optional variables
 - Don't create long full lists; focus on main inputs

4. **Outputs** (### Outputs):
 - Markdown table with columns: Output | Description
 - Extract from module outputs.tf or documentation
 - Include only important/commonly-used output
 - Descriptions should be clear and concise
 - Don't create subsections for required/optional variables
 - Don't create long full lists; focus on main inputs

5. **Usage Example** or **Usage Examples** (### Usage Example / ### Usage Examples):
 - If single example: ### Usage Example
 - If multiple examples: ### Usage Examples, with #### Example {number}: {title} for each
 - Provide 1-2 realistic, practical examples
 - Use HCL code blocks with ```hcl
 - Include common configurations and use cases
 - Add inline comments for clarity where helpful
 - Show integration with other resources when relevant
 - Examples should be copy-paste ready with minimal modifications

Guidelines:
- Maintain consistent formatting across all submodules
- Extract information from source documentation, README, or code
- If information is missing, use "Not documented" or omit optional subsections
- Ensure code examples use correct module source paths
- Include version constraints in examples (e.g., version = "~> 5.0")
- For complex submodules, provide multiple examples showing different use cases
- Keep variable/output tables scannable and well-formatted

Example structure:
## Submodule 1: {name}

### Description
{1-3 sentences about what this submodule does}

### Key Features
- {Feature 1}
- {Feature 2}
- {Feature 3}

### Main Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `var_name` | `type` | `default` | Description |

### Main Outputs

| Output | Description |
|--------|-------------|
| `output_name` | What this outputs |

### Usage Example

```hcl
module "example" {
source = "..."

# Configuration
}

Repeat this structure for each submodule found in the source documentation.
-->

## Best Practices

<!-- TEMPLATE INSTRUCTIONS:
Extract and organize best practices from module documentation, AWS documentation, and industry standards.

Structure:

1. **Identify Practice Categories**:
 - Analyze the module's scope and identify 3-8 logical categories
 - Common categories may include:
   * Resource-specific practices (e.g., "Log Management", "Bucket Configuration")
   * Security and Compliance
   * Performance and Optimization
   * Cost Optimization
   * Operational Excellence
   * Monitoring and Observability
   * Disaster Recovery and High Availability
   * Configuration Management
 - Choose categories relevant to the specific module/service

2. **Category Organization**:
 - Create subsections using ### for each category
 - Format: ### {Category Name}
 - Order categories by importance or logical flow
 - Typically 5-10 best practices per category

3. **Best Practice Format**:
 - Use numbered lists (1., 2., 3., etc.)
 - Each item format: **{Practice Title}**: {Brief explanation}
 - Bold the practice title/summary
 - Follow with colon and 1-2 sentence explanation
 - Be prescriptive (tell what TO do, not just what's possible)
 - Include specific values, thresholds, or recommendations when applicable

4. **Content Guidelines**:
 - Focus on actionable, practical advice
 - Explain WHY (rationale) when not obvious
 - Include specific examples or values where helpful
 - Reference AWS Well-Architected Framework principles when relevant
 - Balance security, cost, performance, and operational concerns
 - Include both "do" and "don't" guidance when helpful

5. **Sources for Best Practices**:
 - Module documentation and examples
 - AWS service-specific best practices documentation
 - AWS Well-Architected Framework
 - Security benchmarks (CIS, NIST)
 - Industry standards and common patterns
 - Performance optimization guides
 - Cost optimization recommendations

6. **Writing Style**:
 - Use imperative mood (command form)
 - Be concise but specific
 - Include concrete examples or metrics when possible
 - Use technical terminology appropriately
 - Maintain consistent structure across all items

7. **General examples of Best Practices**:
 - For a common module, categories might include:
   * Design and Architecture
   * Log Management
   * Alarm Configuration
   * Metric Filters
   * Security
   * Performance
   * Cost Optimization
   * Operational Excellence
   * High Availability and Disaster Recovery
   * Development and Deployment
   * Compliance and Governance

Example structure:

## Best Practices

### {Category 1 Name}
1. **{Practice Title}**: {Explanation with specific guidance}
2. **{Practice Title}**: {Explanation with rationale}
3. **{Practice Title}**: {Explanation with example values}

### {Category 2 Name}
1. **{Practice Title}**: {Explanation}
2. **{Practice Title}**: {Explanation}

If the module documentation lacks best practices:
- Infer from AWS service documentation
- Reference official best practice guides
- Include fundamental security and operational practices
- Focus on common pitfalls and how to avoid them

Aim for 20-50 total best practices across 4-8 categories, depending on module complexity.
-->

## Additional Resources

<!-- TEMPLATE INSTRUCTIONS:
Create a bulleted list of relevant documentation links and resources.

Format: - **{Resource Title}**: {URL}

Essential resources (in order):
1. Module Repository (GitHub)
2. Terraform Registry
3. Module Examples
4. Official service documentation (AWS/Azure/GCP)
5. Service-specific feature pages (if applicable)
6. Best practices/security guides
7. Pricing information

Optional resources:
- API/SDK documentation
- Architecture guides
- Compliance documentation (CIS, HIPAA, etc.)
- Related service documentation

Guidelines:
- Use descriptive, concise titles
- Include 8-15 resources
- Prefer official documentation
- Extract from module README and provider docs
- Verify URLs are current and official
-->


## Notes for AI Agents

When using this module in automated workflows:

1. **Security First**: Always apply least privilege principle
2. **Use Roles Over Users**: Prefer IAM roles with temporary credentials
3. **Encrypt Secrets**: Use PGP for sensitive outputs
4. **Enable MFA**: For privileged access
5. **Tag Consistently**: Implement comprehensive tagging
6. **Monitor Usage**: Enable CloudTrail and set up alerts
7. **Permissions Boundaries**: Use for delegated administration
8. **Session Duration**: Balance security and convenience
9. **Cross-Account Patterns**: Use roles for cross-account access
10. **Modern Auth**: Leverage OIDC and IRSA for CI/CD and Kubernetes
11. **Policy Validation**: Test policies before production
12. **Regular Audits**: Review and rotate credentials regularly
