## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

- [ ] New Databricks bundle/project
- [ ] Bundle configuration update
- [ ] Model/experiment changes
- [ ] Job/pipeline changes
- [ ] Notebook updates
- [ ] Python code changes
- [ ] Documentation updates
- [ ] Bug fix
- [ ] Other (please describe):

## Changed Projects

<!-- List the projects affected by this PR -->

- [ ] `high-risk-wifi`
- [ ] `suspicious-location`
- [ ] Other: ___________

## Changes Made

<!-- Provide detailed information about what was changed -->

### Bundle Configuration
<!-- If databricks.yml or resource files were modified -->
- [ ] Updated environment targets (dev/staging/prod)
- [ ] Modified variables
- [ ] Changed permissions
- [ ] Updated resource definitions
- [ ] Other: ___________

### Code Changes
<!-- If Python code was modified -->
- [ ] Updated model training logic
- [ ] Modified feature engineering
- [ ] Changed inference code
- [ ] Updated data processing
- [ ] Other: ___________

### Infrastructure
<!-- If jobs, pipelines, or serving endpoints were modified -->
- [ ] Updated job schedules or tasks
- [ ] Modified DLT pipelines
- [ ] Changed serving endpoint configuration
- [ ] Updated cluster configurations
- [ ] Other: ___________

## Testing Checklist

- [ ] Bundle validates successfully (`databricks bundle validate -t dev`)
- [ ] Python code passes linting (if applicable)
- [ ] No hardcoded secrets or credentials
- [ ] Required files present (databricks.yml, README.md)
- [ ] YAML syntax is valid
- [ ] Python notebooks compile without errors
- [ ] Changes tested locally (if applicable)

## Deployment Plan

<!-- Describe how these changes should be deployed -->

- [ ] Deploy to dev environment only
- [ ] Deploy to dev, then staging
- [ ] Deploy to all environments (dev → staging → prod)
- [ ] Requires manual intervention: ___________

## Security Considerations

- [ ] No sensitive data in configuration
- [ ] Proper permission levels assigned
- [ ] Service principals configured (for staging/prod)
- [ ] Secrets managed via Databricks secrets or env vars
- [ ] No security vulnerabilities introduced

## Documentation

- [ ] README.md updated (if needed)
- [ ] Configuration changes documented
- [ ] Deployment instructions updated (if needed)
- [ ] Comments added to complex code

## Breaking Changes

<!-- List any breaking changes and migration steps -->

- [ ] No breaking changes
- [ ] Breaking changes (describe below):

<!--
If there are breaking changes, describe:
1. What breaks
2. Why the change is necessary
3. Migration/rollback plan
-->

## Additional Notes

<!-- Any additional context, screenshots, or information -->

## Pre-Merge Checklist

- [ ] All CI checks passing
- [ ] Code reviewed by team member
- [ ] Documentation complete
- [ ] Ready to merge

---

<!--
The following automated checks will run:
- Bundle validation (all environments)
- Python syntax checking
- YAML validation
- Security scanning
- Code quality checks
-->
