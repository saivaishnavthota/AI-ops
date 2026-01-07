# Audit Log - Quick Reference Guide

## ✅ What's Now Logged Automatically

### Authentication Events
- 🟢 **login** - User successfully logged in
- 🔴 **login_failed** - Failed login attempt
- ⚪ **logout** - User logged out

### Other Events (Already Working)
- 📝 **create** - Resource created
- ✏️ **update** - Resource updated
- ✅ **resolve** - Alert/incident resolved
- ▶️ **execute** - Playbook executed
- 👤 **user.role_changed** - User role modified

## 🔍 How to View Login Activity

### Quick Steps
1. Login to http://localhost:7026
2. Click **Settings** in sidebar
3. Click **Audit Log**
4. Filter by Resource Type: **auth**

### What You'll See

**Successful Login:**
```
🟢 LOGIN
User: Michael Chen (admin@demo.com)
Status: SUCCESS
IP: 172.23.0.1
Time: 2026-01-07 12:55:20 PM
Description: User Michael Chen logged in successfully
```

**Failed Login:**
```
🔴 LOGIN FAILED
Email: admin@demo.com
Status: FAILED
IP: 172.23.0.1
Time: 2026-01-07 12:56:15 PM
Error: Invalid email or password
```

**Logout:**
```
⚪ LOGOUT
User: Michael Chen (admin@demo.com)
Status: SUCCESS
IP: 172.23.0.1
Time: 2026-01-07 01:30:45 PM
Description: User Michael Chen logged out
```

## 🚨 Security Monitoring

### Red Flags to Watch For

1. **Multiple Failed Logins**
   - Same email, different IPs
   - Indicates brute force attack
   - Action: Lock account, notify user

2. **Login from Unusual Location**
   - IP from different country
   - Unusual time of day
   - Action: Verify with user

3. **Rapid Login/Logout**
   - Multiple sessions in short time
   - Could indicate credential sharing
   - Action: Review with user

4. **Failed Login After Hours**
   - Login attempts outside business hours
   - Could indicate unauthorized access attempt
   - Action: Investigate immediately

## 📊 Common Filters

### View All Authentication Events
- Resource Type: **auth**

### View Only Failed Logins
- Resource Type: **auth**
- Search: **login_failed**

### View Specific User's Activity
- Search: **user's email or name**

### View Today's Logins
- Resource Type: **auth**
- (Logs are sorted by newest first)

## 💡 Tips

### For Administrators
- ✅ Check audit logs daily for failed login attempts
- ✅ Export logs monthly for compliance
- ✅ Monitor after-hours activity
- ✅ Review IP addresses for unusual patterns

### For Security Teams
- ✅ Set up alerts for multiple failed logins
- ✅ Track login patterns by user
- ✅ Monitor for credential stuffing attacks
- ✅ Review user agents for suspicious activity

### For Operators
- ✅ Use audit logs to troubleshoot user access issues
- ✅ Verify user login history when helping with support
- ✅ Check for system access during incidents

## 📱 What Information is Captured

### For Every Login Event
- ✅ User's full name and email
- ✅ Timestamp (exact date and time)
- ✅ IP address (where they logged in from)
- ✅ User agent (browser and device info)
- ✅ Success or failure status
- ✅ Organization context

### Privacy Note
- ❌ Passwords are NEVER logged
- ❌ Session tokens are NEVER logged
- ✅ Only metadata is captured for security

## 🔧 Troubleshooting

### "I don't see my login"
1. Click the **Refresh** button
2. Make sure you're filtering by Resource Type: **auth**
3. Check you're on page 1
4. Clear any search filters

### "Failed logins aren't showing"
1. Verify you used a valid email address
2. Check the backend is running
3. Try logging in again
4. Refresh the audit log page

### "IP address shows as unknown"
- This is normal for local development
- In production, real IPs will be captured

## 📈 Statistics Dashboard

At the top of the Audit Log page, you'll see:

- **Total Actions Today** - All actions performed today (including logins)
- **Total Actions** - All-time action count
- **Active Users** - Number of unique users with activity

## 🎯 Quick Actions

### Export Login History
1. Filter by Resource Type: **auth**
2. Click **Export** button
3. Save CSV file
4. Open in Excel or Google Sheets

### View Login Details
1. Find the login entry
2. Click the eye icon (👁️)
3. See full details including:
   - Complete timestamp
   - Full IP address
   - Complete user agent string
   - Any error messages (for failed logins)

### Search for User
1. Type user's name or email in search box
2. Press Enter
3. See all their activity including logins

## ⚡ Keyboard Shortcuts

- **Ctrl/Cmd + F** - Focus search box
- **Esc** - Close detail drawer
- **F5** - Refresh page

## 📞 Need Help?

If you have questions about audit logs:
1. Check this guide
2. Review the full user guide (AUDIT_LOGS_USER_GUIDE.md)
3. Contact your system administrator
4. Submit a support ticket

---

**Last Updated:** January 7, 2026
**Feature Status:** ✅ Active and Working
