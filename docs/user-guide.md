# Email Campaign Manager - Complete User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [User Roles](#user-roles)
3. [User Registration & Authentication](#user-registration--authentication)
4. [Complete Email Campaign Flow](#complete-email-campaign-flow)
5. [Step-by-Step Workflows](#step-by-step-workflows)
6. [Best Practices](#best-practices)
7. [Tips & Troubleshooting](#tips--troubleshooting)

---

## Getting Started

### System Requirements
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)
- **Internet**: Stable connection required
- **Account**: Admin must create your account and approve your request

### First Time Access
1. Your admin will send you a registration link
2. Click the link and create your account
3. Verify your email address
4. Wait for admin approval
5. Once approved, you can log in!

---

## User Roles

### 👨‍💼 **Regular User**
- Create email campaigns
- Manage segments and contacts
- Design email templates
- Schedule and send campaigns
- View analytics and insights
- Manage personal SMTP settings

**Permissions:**
- ✅ Create campaigns
- ✅ Create segments
- ✅ Upload contacts
- ✅ Design templates
- ✅ View analytics
- ❌ Cannot manage other users
- ❌ Cannot access admin panel

### 👨‍💻 **Admin User**
- All regular user permissions
- Manage user accounts
- Approve/reject user registration
- Set user permissions
- View system-wide analytics
- Create admin email lists
- Manage SMTP configurations

**Permissions:**
- ✅ Everything regular users can do
- ✅ Manage users
- ✅ Approve registrations
- ✅ Create system-wide email lists
- ✅ View admin dashboard

---

## User Registration & Authentication

### 📋 Registration Flow

```
┌─────────────────┐
│ Admin Creates   │
│ User Account    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ User Receives Email     │
│ with Registration Link  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ User Clicks Link &      │
│ Fills Registration Form │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Verification Email Sent │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ User Verifies Email     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Admin Approves User     │
│ (Approval Notification) │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ ✅ Account Activated    │
│ Ready to Log In!        │
└─────────────────────────┘
```

### 🔓 Login

**How to Log In:**
1. Go to the login page
2. Enter your **username or email**
3. Enter your **password**
4. Click **"Sign In"**
5. Check **"Remember Me"** to stay logged in (optional)

**Forgot Password?**
1. Click "Forgot Password?" on the login page
2. Enter your email address
3. Check your email for password reset link
4. Click the link and create a new password
5. Log in with your new password

---

## Complete Email Campaign Flow

### 🚀 End-to-End Campaign Journey

```
┌──────────────────────┐
│ 1. Set Up Segments   │
│ (Create audience)    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 2. Add Contacts      │
│ (Import email lists) │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 3. Create Template   │
│ (Design email)       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 4. Configure SMTP    │
│ (Email service)      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 5. Create Campaign   │
│ (Set up job)         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 6. Test & Preview    │
│ (Send test email)    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 7. Schedule Campaign │
│ (Set send time)      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 8. Monitor & Analyze │
│ (View analytics)     │
└──────────────────────┘
```

---

## Step-by-Step Workflows

### 📊 Workflow 1: Creating Your First Campaign

#### **Step 1: Create a Segment (Audience)**

1. Log in to the dashboard
2. Click **"Segments"** in the left menu
3. Click **"New Segment"** button
4. Fill in segment details:
   - **Segment Name**: e.g., "Q2 2025 Leads"
   - **Description**: Optional description
5. Click **"Create Segment"**

#### **Step 2: Add Contacts to Segment**

**Option A: Upload CSV File**
1. Click on the segment you just created
2. Click **"Import Contacts"**
3. Select **CSV file** from your computer
4. CSV format should be:
   ```csv
   email,first_name,last_name
   john@example.com,John,Doe
   jane@example.com,Jane,Smith
   ```
5. Click **"Import"** and wait for confirmation

**Option B: Add Contacts Manually**
1. Click on the segment
2. Click **"Add Contact"** button
3. Fill in:
   - **Email**: contact@example.com
   - **First Name**: (optional)
   - **Last Name**: (optional)
4. Click **"Add"**

#### **Step 3: Create an Email Template**

1. Click **"Templates"** in the left menu
2. Click **"New Template"** button
3. Enter **Template Name**: e.g., "Welcome Email"
4. Click **"Design Email"**
5. Use the email editor:
   - Click the **"HTML Source"** button to switch between visual and code view
   - Use the WYSIWYG editor to design your email
   - Add personalization tags like `{{first_name}}`
6. Click **"Save Template"**

#### **Step 4: Configure SMTP**

1. Click **"Settings"** or **"SMTP Configuration"**
2. Click **"Add New SMTP"** or **"Configure"**
3. Enter SMTP details:
   - **SMTP Server**: smtp.gmail.com (or your provider)
   - **Port**: 587 (or 465 for SSL)
   - **Username**: your-email@gmail.com
   - **Password**: Your app-specific password
   - **From Email**: sender@yourdomain.com
   - **From Name**: Your Company Name
4. Click **"Test Connection"** to verify
5. Click **"Save"**

#### **Step 5: Create & Schedule Campaign**

1. Click **"Campaigns"** in the left menu
2. Click **"New Campaign"** button
3. Fill in campaign details:
   - **Campaign Name**: e.g., "Spring Sale 2025"
   - **Subject Line**: e.g., "🌸 Big Spring Sale - 30% Off! 🌸"
   - **Select Template**: Choose the template you created
   - **Select Segment**: Choose your audience
   - **Sender Name**: Override default (optional)
   - **From Email**: Override default (optional)
   - **Reply-To Email**: Optional

4. Click **"Send Test Email"**:
   - Enter YOUR email address
   - Click "Send Test"
   - Check your inbox and preview

5. Schedule the campaign:
   - Choose **Schedule Option**:
     - **Immediate**: Send now
     - **Scheduled**: Send at specific date/time
   - Select date and time using the calendar
   - Click **"Schedule Campaign"**

6. View the confirmation message with:
   - Campaign ID
   - Number of recipients
   - Scheduled send time

#### **Step 6: Monitor Analytics**

1. Click **"Analytics"** in the left menu
2. View real-time campaign metrics:
   - **Total Sent**: Number of emails sent
   - **Delivered**: Successfully delivered
   - **Opened**: How many people opened
   - **Clicked**: How many clicked links
   - **Bounced**: Failed deliveries
   - **Open Rate**: Percentage of opens
   - **Click Rate**: Percentage of clicks

3. Click on a campaign to see detailed analytics

---

### 🎨 Workflow 2: Advanced Email Design

#### **Using Email Editor Features**

**Text Formatting:**
- Select text and use toolbar buttons for bold, italic, underline
- Change font size using dropdown
- Change text color using color picker

**Adding Elements:**
1. **Images**: 
   - Click "Insert Image"
   - Paste URL or upload file
   - Set width and height

2. **Links**:
   - Select text
   - Click "Link" button
   - Enter URL
   - Click "Insert"

3. **Buttons**:
   - Click "Insert Button"
   - Add text and URL
   - Customize color and size

4. **Dividers**:
   - Click "Insert Divider"
   - Customize height and color

**Personalization:**
- Use `{{first_name}}` to insert recipient's first name
- Use `{{last_name}}` for last name
- Use `{{email}}` for email address
- Use `[UNSUBSCRIBE_LINK]` for unsubscribe option

**HTML Mode:**
- Click "HTML Source" to edit raw HTML
- Useful for custom styling or complex layouts

---

### 👥 Workflow 3: Segment Management

#### **Create Dynamic Segments**

1. Navigate to **Segments**
2. Click **"New Segment"**
3. Enter segment name and description
4. Click **"Create Segment"**

#### **Manage Contacts**

**View All Contacts:**
- Click on segment name
- See all contacts in this segment
- Search by email or name

**Export Contacts:**
- Click "Export Contacts" button
- Download as CSV file
- Use for external analysis

**Remove Contacts:**
- Find contact in list
- Click ❌ to remove
- Confirm removal

**De-duplicate:**
- Import contacts
- System automatically prevents duplicates
- Same email won't be added twice

---

### 📈 Workflow 4: Admin Panel

#### **User Management**

**Approve New Users:**
1. Click **"Admin Dashboard"**
2. Click **"User Requests"** or **"Pending Approvals"**
3. Review user details
4. Click **"Approve"** or **"Reject"**
5. Approval email is sent automatically

**Set User Permissions:**
1. Click **"Manage Users"**
2. Find user in list
3. Click **"Edit Permissions"**
4. Check/uncheck permissions:
   - ✅ Can create campaigns
   - ✅ Can manage templates
   - ✅ Can import contacts
   - ✅ Can view analytics
5. Click **"Save"**

**Deactivate/Activate User:**
1. Click **"Manage Users"**
2. Click **"Deactivate"** next to user
3. User can no longer log in
4. To reactivate, click **"Activate"**

#### **Create Admin Email Lists**

1. Click **"Admin Email Lists"**
2. Click **"Create New List"**
3. Enter:
   - **List Name**: e.g., "VIP Customers"
   - **Description**: Optional
4. Click **"Create"**
5. Add contacts (same as segments)
6. Use in admin campaigns

#### **View System Analytics**

1. Click **"Analytics"** in admin menu
2. View:
   - Total emails sent
   - Overall open rates
   - Overall click rates
   - Active campaigns
   - Top performing campaigns

---

## Best Practices

### ✅ **Email Content**

1. **Subject Line**
   - Keep under 50 characters for mobile
   - Use clear, compelling language
   - Avoid spam trigger words
   - Include relevant keywords

2. **Preview Text**
   - Add summary after subject
   - Keep under 100 characters
   - Give reason to open

3. **Email Design**
   - Use responsive design (mobile-friendly)
   - Keep images under 2MB
   - Use alt text for all images
   - Limit to 2-3 colors max
   - Use readable fonts (Arial, Verdana, Georgia)

### ✅ **Segment Best Practices**

1. **Segmentation Strategy**
   - Segment by behavior (recent buyers, inactive)
   - Segment by demographics (location, age)
   - Segment by engagement (openers, clickers)

2. **List Hygiene**
   - Remove bounced emails regularly
   - Remove unsubscribers immediately
   - Keep list updated monthly

3. **Avoid Spam Lists**
   - Don't purchase email lists
   - Only use opted-in contacts
   - Respect unsubscribe requests

### ✅ **Scheduling Best Practices**

1. **Optimal Send Times**
   - Tuesday-Thursday generally best
   - 9-10 AM or 6-7 PM common
   - Test different times
   - Consider recipient timezone if possible

2. **Frequency**
   - Don't send more than 2x per week
   - Space out campaigns by at least 3 days
   - Monitor unsubscribe rates

3. **Testing**
   - Always send test email first
   - Check on desktop and mobile
   - Test all links work
   - Verify personalization tags work

### ✅ **Analytics Review**

1. **Key Metrics to Monitor**
   - Open rate (target: 20-30%)
   - Click rate (target: 2-5%)
   - Bounce rate (target: <1%)
   - Unsubscribe rate (target: <0.5%)

2. **Optimization**
   - If low open rate: Improve subject lines
   - If low click rate: Improve CTA buttons
   - If high bounce: Clean your list
   - If high unsubscribe: Reduce frequency

---

## Tips & Troubleshooting

### 📧 **Email Not Sending**

**Problem**: Campaign stuck in "pending"
- **Solution 1**: Verify SMTP credentials are correct
- **Solution 2**: Check if port 587 is not blocked
- **Solution 3**: Use app-specific password (Gmail)
- **Solution 4**: Contact support with campaign ID

**Problem**: Emails going to spam
- **Solution 1**: Add authentication (SPF, DKIM, DMARC)
- **Solution 2**: Improve subject line (avoid caps, special chars)
- **Solution 3**: Remove invalid emails from list
- **Solution 4**: Build sender reputation gradually

### 👤 **Account Issues**

**Problem**: Can't log in
- **Solution 1**: Check caps lock on password
- **Solution 2**: Use email instead of username
- **Solution 3**: Reset password using "Forgot Password"
- **Solution 4**: Contact admin to activate account

**Problem**: Email verification not received
- **Solution 1**: Check spam/promotions folder
- **Solution 2**: Request new verification email
- **Solution 3**: Contact admin support

### 📋 **Data Issues**

**Problem**: CSV import not working
- **Solution 1**: Ensure CSV has headers: email, first_name, last_name
- **Solution 2**: Check for special characters in names
- **Solution 3**: Ensure emails are valid format
- **Solution 4**: Try upload with smaller file (test first)

**Problem**: Duplicate contacts appearing
- **Solution 1**: System prevents exact duplicates automatically
- **Solution 2**: May have slight variations (spaces, case)
- **Solution 3**: Export and manually clean in Excel

### 🔧 **Technical Issues**

**Problem**: Page loading slowly
- **Solution 1**: Clear browser cache (Ctrl+Shift+Del)
- **Solution 2**: Try different browser
- **Solution 3**: Check internet connection
- **Solution 4**: Refresh page

**Problem**: Changes not saving
- **Solution 1**: Check for error messages in red
- **Solution 2**: Ensure all required fields filled
- **Solution 3**: Try again after waiting 30 seconds
- **Solution 4**: Contact support

---

## Feature Overview

### 📊 Dashboard
- Quick overview of recent campaigns
- Active campaigns counter
- Recent email opens and clicks
- Quick action buttons

### 📧 Email Templates
- Create and manage templates
- Visual and HTML editors
- Template preview
- Duplicate templates for quick setup

### 👥 Segments
- Create targeted audience groups
- Import contacts from CSV
- Manage individual contacts
- Export segment data

### 📤 Campaigns
- Design and schedule campaigns
- Select template and segment
- Customize sender info
- Send test emails
- Schedule for future delivery

### 📈 Analytics
- View campaign performance
- Track opens and clicks
- Monitor delivery stats
- Drill down into details

### ⚙️ Settings
- Manage SMTP configuration
- Update profile information
- Change password
- View account activity

### 🔐 Admin Panel
- Manage user accounts
- Approve registration requests
- Set user permissions
- Create admin email lists
- View system-wide analytics

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save current form |
| `Ctrl+B` | Bold text in editor |
| `Ctrl+I` | Italic text in editor |
| `Ctrl+U` | Underline text in editor |
| `Esc` | Close modal/dialog |
| `Tab` | Navigate between fields |

---

## Getting Help

### 📞 Support Resources
1. **In-App Help**: Hover over question marks (?) for tooltips
2. **Documentation**: Visit our GitHub Pages
3. **Contact Admin**: Use "Contact Support" form
4. **Bug Report**: Report issues with details at info@company.com

---

## Summary Checklist

### Before Sending First Campaign
- [ ] Account approved by admin
- [ ] Email verified
- [ ] Segment created with contacts
- [ ] Email template designed
- [ ] SMTP configured and tested
- [ ] Test email sent successfully

### Before Scheduling Campaign
- [ ] Subject line is compelling
- [ ] Email looks good on mobile
- [ ] All links tested
- [ ] Personalization tags working
- [ ] Unsubscribe link included
- [ ] Send time is reasonable

### After Campaign Sends
- [ ] Monitor delivery in next hour
- [ ] Check for bounces
- [ ] Review open rate after 24 hours
- [ ] Review click rate after 48 hours
- [ ] Document learnings for next campaign

---

**Last Updated**: April 14, 2026  
**Version**: 1.0

For more information, visit: [GitHub Repository](https://github.com/narendrancs89/EmailCampaignManager)
