#!/usr/bin/env python3
"""
Seed script for Knowledge Base articles.
"""
import sys
import os
import asyncio
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import AsyncSessionLocal
from app.models import Organization, User, KnowledgeBaseArticle


async def seed_kb_articles(db: AsyncSession, org_id: str, author_id: str):
    """Seed KB articles data."""
    print("Seeding KB articles...")
    
    kb_articles_data = [
        {
            "title": "How to Reset Your Password",
            "excerpt": "Step-by-step guide to reset your password when you can't access your account",
            "content": """# How to Reset Your Password

If you're unable to access your account due to a forgotten password, follow these steps:

## Method 1: Self-Service Password Reset

1. Go to the login page
2. Click on "Forgot Password?" link
3. Enter your email address
4. Check your email for reset instructions
5. Click the reset link in the email
6. Create a new strong password

## Method 2: Contact IT Support

If the self-service method doesn't work:

1. Contact IT support at support@company.com
2. Provide your username and employee ID
3. Verify your identity with security questions
4. IT will reset your password and send temporary credentials

## Password Requirements

- Minimum 8 characters
- Must include uppercase and lowercase letters
- Must include at least one number
- Must include at least one special character
- Cannot be the same as your last 5 passwords

## Troubleshooting

**Problem**: Not receiving reset email
**Solution**: Check spam folder, verify email address is correct

**Problem**: Reset link expired
**Solution**: Request a new reset link (links expire after 1 hour)

**Problem**: New password not accepted
**Solution**: Ensure password meets all requirements listed above
""",
            "category": "Access Issue",
            "tags": ["password", "login", "access", "security", "account"],
            "views": 245,
            "helpful_count": 89,
            "is_published": True,
        },
        {
            "title": "Email Server Connection Issues",
            "excerpt": "Troubleshooting guide for email connectivity problems and server timeouts",
            "content": """# Email Server Connection Issues

This guide helps resolve common email server connectivity problems.

## Common Symptoms

- Cannot send or receive emails
- Email client shows "connection timeout" errors
- Emails stuck in outbox
- Authentication failures

## Quick Fixes

### Check Internet Connection
1. Verify internet connectivity
2. Try accessing other websites
3. Restart your router if needed

### Verify Email Settings
- **Incoming Server (IMAP)**: mail.company.com, Port 993, SSL
- **Outgoing Server (SMTP)**: smtp.company.com, Port 587, TLS
- **Authentication**: Use same credentials as login

### Clear Email Cache
1. Close email client completely
2. Clear application cache/data
3. Restart the email application
4. Re-enter account credentials

## Advanced Troubleshooting

### Check Firewall Settings
- Ensure ports 993 (IMAP) and 587 (SMTP) are open
- Add email client to firewall exceptions
- Temporarily disable antivirus email scanning

### DNS Issues
1. Flush DNS cache: `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (Mac)
2. Try using Google DNS (8.8.8.8, 8.8.4.4)
3. Contact network administrator if issues persist

### Server Status
Check our status page at status.company.com for any ongoing email server maintenance.

## When to Contact Support

Contact IT support if:
- Issues persist after trying all troubleshooting steps
- Multiple users report the same problem
- Error messages mention server-side issues
- You need help configuring email clients

**Support Email**: support@company.com
**Phone**: (555) 123-4567
**Priority**: High for email issues affecting multiple users
""",
            "category": "infrastructure",
            "tags": ["email", "server", "connection", "timeout", "smtp", "imap", "troubleshooting"],
            "views": 156,
            "helpful_count": 67,
            "is_published": True,
        },
        {
            "title": "Database Performance Optimization",
            "excerpt": "Best practices and techniques for improving database query performance and reducing load times",
            "content": """# Database Performance Optimization

Learn how to optimize database performance and resolve slow query issues.

## Identifying Performance Issues

### Common Symptoms
- Slow application response times
- Database timeouts
- High CPU usage on database server
- Long-running queries
- Connection pool exhaustion

### Monitoring Tools
- Use database performance monitoring dashboards
- Check slow query logs
- Monitor connection counts
- Review CPU and memory usage

## Query Optimization

### Index Optimization
1. **Identify missing indexes**
   ```sql
   EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user@example.com';
   ```

2. **Create appropriate indexes**
   ```sql
   CREATE INDEX idx_users_email ON users(email);
   ```

3. **Remove unused indexes** to improve write performance

### Query Best Practices
- Use LIMIT clauses for large result sets
- Avoid SELECT * - specify only needed columns
- Use appropriate WHERE clauses
- Consider query caching for frequently accessed data

## Connection Management

### Connection Pooling
- Configure appropriate pool sizes
- Set reasonable connection timeouts
- Monitor pool utilization
- Use connection pooling libraries

### Connection Limits
- Review max_connections setting
- Monitor active connections
- Implement connection retry logic
- Close connections properly in application code

## Maintenance Tasks

### Regular Maintenance
- **Daily**: Monitor performance metrics
- **Weekly**: Review slow query logs
- **Monthly**: Update table statistics
- **Quarterly**: Review and optimize indexes

### Database Cleanup
1. Archive old data
2. Remove unnecessary logs
3. Rebuild fragmented indexes
4. Update database statistics

## Emergency Procedures

### High Load Situations
1. Identify resource-intensive queries
2. Kill long-running queries if necessary
3. Implement query throttling
4. Scale database resources if needed

### Connection Issues
1. Check connection pool status
2. Restart application servers if needed
3. Verify database server health
4. Review network connectivity

## Performance Tuning Checklist

- [ ] Indexes are optimized for common queries
- [ ] Connection pooling is properly configured
- [ ] Slow queries are identified and optimized
- [ ] Database statistics are up to date
- [ ] Monitoring and alerting are in place
- [ ] Regular maintenance tasks are scheduled

## Getting Help

For complex database issues:
- Contact Database Administrator team
- Provide slow query logs and performance metrics
- Include application error messages
- Specify affected time periods

**DBA Team**: dba@company.com
**Escalation**: For production issues affecting multiple users
""",
            "category": "Performance",
            "tags": ["database", "performance", "optimization", "queries", "indexing", "troubleshooting"],
            "views": 89,
            "helpful_count": 34,
            "is_published": True,
        },
        {
            "title": "VPN Connection Setup and Troubleshooting",
            "excerpt": "Complete guide for setting up VPN connections and resolving common connectivity issues",
            "content": """# VPN Connection Setup and Troubleshooting

This guide covers VPN setup and common connection issues.

## Initial Setup

### Windows Setup
1. Open Settings > Network & Internet > VPN
2. Click "Add a VPN connection"
3. Enter connection details:
   - **VPN Provider**: Windows (built-in)
   - **Connection Name**: Company VPN
   - **Server**: vpn.company.com
   - **VPN Type**: IKEv2
   - **Username/Password**: Your domain credentials

### macOS Setup
1. Open System Preferences > Network
2. Click "+" to add new connection
3. Select "VPN" and "IKEv2"
4. Enter server address and authentication details
5. Click "Connect"

### Mobile Setup
Download and configure the company VPN app from your device's app store.

## Common Issues and Solutions

### Cannot Connect to VPN

**Symptoms**: Connection fails immediately or times out

**Solutions**:
1. Verify internet connection
2. Check VPN server address spelling
3. Confirm username/password are correct
4. Try different VPN protocols (IKEv2, OpenVPN, L2TP)
5. Restart network adapter
6. Temporarily disable firewall/antivirus

### Connected but No Internet Access

**Symptoms**: VPN shows connected but websites don't load

**Solutions**:
1. Check DNS settings
2. Flush DNS cache
3. Restart VPN connection
4. Try different DNS servers (8.8.8.8, 1.1.1.1)
5. Verify routing table

### Slow VPN Performance

**Symptoms**: Internet is very slow when VPN is connected

**Solutions**:
1. Try different VPN server locations
2. Change VPN protocol
3. Close unnecessary applications
4. Check for background downloads
5. Contact IT for server load information

### Frequent Disconnections

**Symptoms**: VPN disconnects randomly

**Solutions**:
1. Update VPN client software
2. Adjust power management settings
3. Check for network adapter driver updates
4. Configure auto-reconnect if available
5. Switch to more stable VPN protocol

## Security Best Practices

### While Using VPN
- Always verify VPN is connected before accessing company resources
- Don't disable VPN to access blocked content
- Report any suspicious network activity
- Keep VPN client software updated

### Troubleshooting Security
- Never share VPN credentials
- Use strong, unique passwords
- Enable two-factor authentication if available
- Report lost/stolen devices immediately

## Advanced Configuration

### Split Tunneling
Configure which traffic goes through VPN:
1. Open VPN client settings
2. Find "Split Tunneling" or "Bypass VPN"
3. Add applications or websites to bypass
4. Save and reconnect

### Custom DNS
For better performance:
1. Set custom DNS servers in VPN settings
2. Recommended: 8.8.8.8, 8.8.4.4 (Google)
3. Alternative: 1.1.1.1, 1.0.0.1 (Cloudflare)

## Getting Support

### Before Contacting Support
1. Note exact error messages
2. Try basic troubleshooting steps
3. Check if issue affects multiple devices
4. Document when the problem started

### Contact Information
- **IT Helpdesk**: (555) 123-4567
- **Email**: vpn-support@company.com
- **Priority**: High for remote workers unable to connect

### Information to Provide
- Operating system and version
- VPN client version
- Error messages (screenshots helpful)
- Network environment (home, office, public WiFi)
- Time when issue occurred
""",
            "category": "Access Issue",
            "tags": ["vpn", "connection", "remote", "access", "network", "security", "troubleshooting"],
            "views": 178,
            "helpful_count": 72,
            "is_published": True,
        },
        {
            "title": "Software Installation and Updates",
            "excerpt": "Guide for installing approved software and managing updates on company devices",
            "content": """# Software Installation and Updates

This guide covers software installation policies and procedures.

## Software Installation Policy

### Approved Software
- Only install software from the approved software list
- Use company software center when available
- Request approval for new software through IT portal

### Prohibited Software
- Peer-to-peer file sharing applications
- Unauthorized remote access tools
- Cracked or pirated software
- Software from untrusted sources

## Installation Procedures

### Using Software Center (Recommended)
1. Open Company Software Center
2. Browse or search for required software
3. Click "Install" for approved applications
4. Wait for automatic installation
5. Restart if prompted

### Manual Installation
For approved software not in Software Center:
1. Download from official vendor website only
2. Verify digital signatures
3. Run installer as administrator
4. Follow installation wizard
5. Register software if required

### Mobile Devices
- Use official app stores (Google Play, Apple App Store)
- Avoid sideloading applications
- Check app permissions before installing
- Keep apps updated

## Update Management

### Automatic Updates
- Enable automatic updates for operating system
- Allow automatic updates for security software
- Configure update schedules during off-hours

### Manual Updates
1. Check for updates regularly
2. Read update notes for important changes
3. Backup important data before major updates
4. Test critical applications after updates

### Update Priorities
1. **Critical Security Updates**: Install immediately
2. **Security Updates**: Install within 48 hours
3. **Feature Updates**: Install during maintenance windows
4. **Optional Updates**: Install as needed

## Troubleshooting Installation Issues

### Common Problems

**Installation Fails**
- Run as administrator
- Temporarily disable antivirus
- Check available disk space
- Verify system requirements

**Software Won't Start**
- Check for missing dependencies
- Run compatibility troubleshooter
- Verify user permissions
- Check event logs for errors

**Update Failures**
- Restart and retry
- Clear update cache
- Check internet connection
- Run Windows Update troubleshooter

### Error Codes
- **Error 1603**: Generic installer error - check logs
- **Error 1722**: Windows Installer service issue
- **Error 2**: File not found - verify download integrity

## Software Requests

### Requesting New Software
1. Submit request through IT portal
2. Provide business justification
3. Include software details and vendor information
4. Wait for approval before installation

### Request Information Needed
- Software name and version
- Vendor/publisher information
- Business purpose and users
- Cost and licensing requirements
- Security and compliance considerations

## License Management

### License Compliance
- Only install software you're licensed to use
- Don't share license keys
- Report unused software for license optimization
- Comply with vendor license terms

### License Types
- **Per-device**: Licensed to specific computer
- **Per-user**: Licensed to specific user
- **Concurrent**: Limited number of simultaneous users
- **Site**: Unlimited use within organization

## Security Considerations

### Safe Installation Practices
- Download only from official sources
- Verify digital signatures
- Read permissions and privacy policies
- Avoid bundled software/toolbars
- Keep installation files for reinstallation

### Red Flags
- Requests for unnecessary permissions
- No digital signature or unknown publisher
- Bundled with other software
- Requires disabling security software
- Free versions of expensive commercial software

## Getting Help

### Self-Service Resources
- Company Software Center
- IT Knowledge Base
- Software vendor documentation
- Online tutorials and guides

### IT Support
Contact IT for:
- Software approval requests
- Installation failures
- License questions
- Security concerns

**IT Helpdesk**: (555) 123-4567
**Software Requests**: software-requests@company.com
**License Questions**: licensing@company.com

### Emergency Software Needs
For urgent business-critical software:
1. Contact IT immediately
2. Explain business impact
3. Provide temporary approval justification
4. Follow up with formal request
""",
            "category": "Service Request",
            "tags": ["software", "installation", "updates", "licensing", "security", "policy"],
            "views": 134,
            "helpful_count": 45,
            "is_published": True,
        },
    ]
    
    for article_data in kb_articles_data:
        article = KnowledgeBaseArticle(
            organization_id=org_id,
            author_id=author_id,
            **article_data
        )
        db.add(article)
    
    await db.commit()
    print(f"✓ Created {len(kb_articles_data)} KB articles")


async def main():
    """Main seeding function."""
    async with AsyncSessionLocal() as db:
        try:
            # Get the first organization and admin user
            from sqlalchemy import select
            
            result = await db.execute(select(Organization))
            org = result.scalars().first()
            
            if not org:
                print("❌ No organization found. Please run the main seed script first.")
                return
            
            result = await db.execute(
                select(User).filter(
                    User.organization_id == org.id,
                    User.role == "admin"
                )
            )
            admin_user = result.scalars().first()
            
            if not admin_user:
                print("❌ No admin user found. Please run the main seed script first.")
                return
            
            print(f"Seeding KB articles for organization: {org.name}")
            
            # Seed KB articles
            await seed_kb_articles(db, str(org.id), str(admin_user.id))
            
            print("\n✅ KB articles seeding completed successfully!")
            print("\nTest the relevance filtering by creating tickets with these subjects:")
            print("- 'Cannot login to my account' (should match password reset article)")
            print("- 'Email not working, connection timeout' (should match email server article)")
            print("- 'Database is very slow' (should match database performance article)")
            print("- 'VPN won't connect from home' (should match VPN troubleshooting article)")
            print("- 'Need to install new software' (should match software installation article)")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())