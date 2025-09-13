# 🔒 Security Guide for CO2 Shopping Assistant

## ⚠️ **CRITICAL: Before Committing to Public Repository**

### **1. Never Commit These Files:**
- `terraform.tfvars` (contains real project IDs and sensitive config)
- `*.tfstate` files (contain infrastructure state)
- `*.key`, `*.pem`, `*.json` files with credentials
- `.env` files with API keys
- Any files containing real project IDs or API keys

### **2. Required Setup Before Deployment:**

#### **A. Create `terraform/terraform.tfvars`:**
```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform.tfvars with your actual values
```

#### **B. Update `terraform/backend.hcl`:**
```bash
# Change "tfstate-YOUR-PROJECT-ID" to your actual bucket name
bucket = "tfstate-your-actual-project-id"
```

#### **C. Set Environment Variables:**
```bash
export GOOGLE_AI_API_KEY="your-gemini-api-key"
export GOOGLE_PROJECT_ID="your-gcp-project-id"
```

### **3. Security Best Practices:**

#### **API Keys & Secrets:**
- Store API keys in environment variables
- Use Kubernetes secrets for sensitive data
- Never hardcode credentials in source code

#### **Infrastructure:**
- Use least-privilege IAM roles
- Enable audit logging
- Use private clusters when possible
- Enable network policies

#### **Container Security:**
- Use non-root users in containers
- Scan images for vulnerabilities
- Keep base images updated
- Use minimal base images

### **4. Deployment Security:**

#### **Before First Deployment:**
1. ✅ Create `terraform.tfvars` with your values
2. ✅ Update `backend.hcl` with your bucket name
3. ✅ Set environment variables
4. ✅ Verify `.gitignore` excludes sensitive files
5. ✅ Test deployment in development environment

#### **Production Considerations:**
- Use separate GCP projects for dev/staging/prod
- Enable Cloud Security Command Center
- Set up monitoring and alerting
- Implement backup and disaster recovery
- Use managed certificates for HTTPS

### **5. Monitoring & Compliance:**

#### **Security Monitoring:**
- Enable Cloud Audit Logs
- Set up Security Command Center
- Monitor for unusual API usage
- Track certificate expiration

#### **Compliance:**
- Follow GDPR guidelines for user data
- Implement data retention policies
- Ensure CO2 data accuracy and transparency
- Document data processing activities

## 🚀 **Quick Start (Secure)**

```bash
# 1. Clone and setup
git clone https://github.com/prabhakaran-jm/co2-shopping-assistant.git
cd co2-shopping-assistant

# 2. Configure secrets
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform.tfvars with your values

# 3. Update backend
# Edit terraform/backend.hcl with your bucket name

# 4. Deploy
./scripts/deploy-infra.sh --project-id YOUR_PROJECT_ID --gemini-api-key YOUR_API_KEY
```

## 📞 **Security Issues**

If you find security vulnerabilities:
1. **DO NOT** create public issues
2. Email security concerns privately
3. Follow responsible disclosure practices

---

**Remember: Security is everyone's responsibility! 🔒**
