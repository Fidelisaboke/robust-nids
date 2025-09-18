"""
Settings Page - System configuration and preferences
"""

import streamlit as st
from datetime import datetime

def show():
    """Render the settings page"""

    st.header("⚙️ System Settings & Configuration")

    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Detection Settings",
        "Alert Configuration",
        "Data Management",
        "User Management",
        "System Maintenance"
    ])

    with tab1:
        show_detection_settings()

    with tab2:
        show_alert_configuration()

    with tab3:
        show_data_management()

    with tab4:
        show_user_management()

    with tab5:
        show_system_maintenance()

def show_detection_settings():
    """Display detection engine configuration"""

    st.subheader("Detection Engine Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Model Settings")

        detection_threshold = st.slider(
            "Detection Threshold",
            min_value=0.1, max_value=1.0, value=0.85, step=0.05,
            help="Minimum confidence score for threat detection"
        )

        false_positive_tolerance = st.slider(
            "False Positive Tolerance",
            min_value=0.01, max_value=0.10, value=0.02, step=0.01,
            help="Acceptable false positive rate"
        )

        batch_processing_size = st.number_input(
            "Batch Processing Size",
            min_value=100, max_value=10000, value=1000, step=100,
            help="Number of packets processed in each batch"
        )

        model_update_frequency = st.selectbox(
            "Model Update Frequency",
            ["Real-time", "Hourly", "Daily", "Weekly", "Manual"],
            index=2,
            help="How often the model should be retrained"
        )

        # Adversarial defense settings
        st.markdown("**Adversarial Defense Settings**")

        enable_adversarial_detection = st.checkbox(
            "Enable Adversarial Attack Detection",
            value=True,
            help="Detect potential adversarial attacks on the model"
        )

        adversarial_threshold = st.slider(
            "Adversarial Detection Sensitivity",
            min_value=0.1, max_value=1.0, value=0.7, step=0.1,
            help="Sensitivity for detecting adversarial examples"
        )

    with col2:
        st.subheader("Traffic Analysis Settings")

        enable_deep_inspection = st.checkbox(
            "Deep Packet Inspection",
            value=True,
            help="Enable detailed packet content analysis"
        )

        enable_behavioral_analysis = st.checkbox(
            "Behavioral Analysis",
            value=True,
            help="Analyze traffic patterns and behaviors"
        )

        flow_timeout = st.number_input(
            "Flow Timeout (seconds)",
            min_value=30, max_value=3600, value=300,
            help="Time before inactive flows are closed"
        )

        max_concurrent_flows = st.number_input(
            "Maximum Concurrent Flows",
            min_value=1000, max_value=1000000, value=50000,
            help="Maximum number of flows to track simultaneously"
        )

        # Protocol-specific settings
        st.markdown("**Protocol-Specific Settings**")

        protocols_to_analyze = st.multiselect(
            "Protocols to Analyze",
            ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "DNS", "SSH", "FTP", "SMTP"],
            default=["TCP", "UDP", "HTTP", "HTTPS", "DNS"],
            help="Network protocols to include in analysis"
        )

        http_inspection_depth = st.selectbox(
            "HTTP Inspection Depth",
            ["Headers Only", "Headers + Body", "Full Content"],
            index=1,
            help="Level of HTTP traffic inspection"
        )

    # Feature engineering settings
    st.markdown("---")
    st.subheader("Feature Engineering Settings")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Statistical Features**")
        enable_statistical_features = st.checkbox("Statistical Features", value=True)
        enable_time_series_features = st.checkbox("Time Series Features", value=True)
        window_size = st.number_input("Window Size (packets)", 1, 1000, 100)

    with col2:
        st.markdown("**Network Features**")
        enable_port_analysis = st.checkbox("Port Analysis", value=True)
        enable_ip_geolocation = st.checkbox("IP Geolocation", value=True)
        enable_dns_analysis = st.checkbox("DNS Analysis", value=True)

    with col3:
        st.markdown("**Advanced Features**")
        enable_entropy_features = st.checkbox("Entropy Features", value=True)
        enable_graph_features = st.checkbox("Graph Features", value=False)
        enable_ml_features = st.checkbox("ML-derived Features", value=True)

    # Save settings
    if st.button("💾 Save Detection Settings", type="primary"):
        settings = {
            "detection_threshold": detection_threshold,
            "false_positive_tolerance": false_positive_tolerance,
            "batch_processing_size": batch_processing_size,
            "model_update_frequency": model_update_frequency,
            "enable_adversarial_detection": enable_adversarial_detection,
            "adversarial_threshold": adversarial_threshold,
            "updated_at": datetime.now().isoformat()
        }
        st.success("Detection settings saved successfully!")
        with st.expander("View Saved Configuration"):
            st.json(settings)

def show_alert_configuration():
    """Display alert system configuration"""

    st.subheader("Alert System Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Alert Thresholds")

        # Severity thresholds
        critical_threshold = st.slider(
            "Critical Alert Threshold",
            min_value=0.90, max_value=1.0, value=0.98, step=0.01,
            help="Confidence threshold for critical alerts"
        )

        high_threshold = st.slider(
            "High Priority Threshold",
            min_value=0.70, max_value=0.95, value=0.90, step=0.01,
            help="Confidence threshold for high priority alerts"
        )

        medium_threshold = st.slider(
            "Medium Priority Threshold",
            min_value=0.50, max_value=0.85, value=0.75, step=0.01,
            help="Confidence threshold for medium priority alerts"
        )

        # Alert rate limiting
        st.markdown("**Rate Limiting**")

        max_alerts_per_minute = st.number_input(
            "Max Alerts per Minute",
            min_value=1, max_value=1000, value=50,
            help="Maximum number of alerts to generate per minute"
        )

        duplicate_suppression_window = st.number_input(
            "Duplicate Suppression (minutes)",
            min_value=1, max_value=60, value=5,
            help="Time window to suppress duplicate alerts"
        )

    with col2:
        st.subheader("Notification Settings")

        # Email notifications
        enable_email_notifications = st.checkbox("Enable Email Notifications", value=True)

        if enable_email_notifications:
            email_recipients = st.text_area(
                "Email Recipients (one per line)",
                value="admin@company.com\nsecurity@company.com",
                height=100
            )

            email_for_critical = st.checkbox("Email for Critical Alerts", value=True)
            email_for_high = st.checkbox("Email for High Priority Alerts", value=True)
            email_for_medium = st.checkbox("Email for Medium Priority Alerts", value=False)

        # Slack/Teams integration
        enable_slack = st.checkbox("Enable Slack Integration", value=False)
        if enable_slack:
            slack_webhook = st.text_input("Slack Webhook URL", type="password")
            slack_channel = st.text_input("Slack Channel", value="#security-alerts")

        enable_teams = st.checkbox("Enable Microsoft Teams", value=False)
        if enable_teams:
            teams_webhook = st.text_input("Teams Webhook URL", type="password")

    # Alert automation
    st.markdown("---")
    st.subheader("Alert Automation & Response")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Automated Responses**")

        auto_block_critical = st.checkbox("Auto-block Critical Threats", value=False)
        auto_quarantine = st.checkbox("Auto-quarantine Suspicious Files", value=False)
        auto_incident_creation = st.checkbox("Auto-create Security Incidents", value=True)

        escalation_enabled = st.checkbox("Enable Alert Escalation", value=True)
        if escalation_enabled:
            escalation_time = st.number_input("Escalation Time (minutes)", 1, 1440, 30)

    with col2:
        st.markdown("**Integration Settings**")

        siem_integration = st.checkbox("SIEM Integration", value=False)
        if siem_integration:
            siem_type = st.selectbox("SIEM Platform", ["Splunk", "QRadar", "ArcSight", "LogRhythm"])
            siem_endpoint = st.text_input("SIEM Endpoint URL")

        soar_integration = st.checkbox("SOAR Integration", value=False)
        if soar_integration:
            soar_platform = st.selectbox("SOAR Platform", ["Phantom", "Demisto", "Resilient"])

    # Custom alert rules
    st.subheader("Custom Alert Rules")

    with st.expander("Add Custom Rule"):
        rule_name = st.text_input("Rule Name")
        rule_condition = st.text_area("Condition (Python expression)",
                                     placeholder="confidence > 0.9 and src_ip.startswith('192.168')")
        rule_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        rule_action = st.selectbox("Action", ["Alert Only", "Block IP", "Quarantine", "Custom Script"])

        if st.button("Add Rule"):
            st.success(f"Custom rule '{rule_name}' added successfully!")

def show_data_management():
    """Display data management and retention settings"""

    st.subheader("Data Management & Retention")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Data Retention Policies")

        raw_data_retention = st.selectbox(
            "Raw Traffic Data Retention",
            ["7 days", "30 days", "90 days", "1 year", "Indefinite"],
            index=2
        )

        alert_data_retention = st.selectbox(
            "Alert Data Retention",
            ["30 days", "90 days", "1 year", "3 years", "Indefinite"],
            index=3
        )

        model_data_retention = st.selectbox(
            "Model Training Data Retention",
            ["90 days", "1 year", "3 years", "Indefinite"],
            index=2
        )

        log_retention = st.selectbox(
            "System Log Retention",
            ["30 days", "90 days", "1 year", "3 years"],
            index=1
        )

        # Data compression
        st.markdown("**Data Compression**")
        enable_compression = st.checkbox("Enable Data Compression", value=True)
        if enable_compression:
            compression_algorithm = st.selectbox("Compression Algorithm",
                                               ["gzip", "lz4", "zstd"], index=2)
            compression_level = st.slider("Compression Level", 1, 9, 6)

    with col2:
        st.subheader("Data Storage Settings")

        # Storage locations
        primary_storage = st.text_input("Primary Storage Path", value="/data/nids/primary")
        backup_storage = st.text_input("Backup Storage Path", value="/data/nids/backup")
        archive_storage = st.text_input("Archive Storage Path", value="/data/nids/archive")

        # Database settings
        st.markdown("**Database Configuration**")
        db_type = st.selectbox("Database Type", ["PostgreSQL", "MySQL", "MongoDB", "InfluxDB"])
        db_host = st.text_input("Database Host", value="localhost")
        db_port = st.number_input("Database Port", 1, 65535, 5432)

        # Backup settings
        st.markdown("**Backup Configuration**")
        enable_auto_backup = st.checkbox("Enable Automatic Backups", value=True)
        if enable_auto_backup:
            backup_frequency = st.selectbox("Backup Frequency",
                                          ["Hourly", "Daily", "Weekly"], index=1)
            backup_retention = st.number_input("Backup Retention (days)", 1, 365, 30)

    # Data export/import
    st.markdown("---")
    st.subheader("Data Export & Import")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Export Data**")
        export_format = st.selectbox("Export Format", ["CSV", "JSON", "Parquet", "SQL"])
        export_date_range = st.date_input("Export Date Range", value=[])

        if st.button("📤 Export Data"):
            st.success("Data export initiated. Download link will be available shortly.")

    with col2:
        st.markdown("**Import Data**")
        uploaded_file = st.file_uploader("Choose file to import", type=['csv', 'json', 'parquet'])
        if uploaded_file:
            import_validation = st.checkbox("Validate on Import", value=True)
            if st.button("📥 Import Data"):
                st.success("Data import initiated. Processing in background.")

    with col3:
        st.markdown("**Data Migration**")
        migration_target = st.selectbox("Migration Target", ["New Database", "Cloud Storage", "External System"])

        if st.button("🔄 Start Migration"):
            st.info("Data migration process started. This may take some time.")

    # Storage usage statistics
    st.subheader("Storage Usage Statistics")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Raw Data", "2.3 TB", "45 GB ↑")
    with col2:
        st.metric("Processed Data", "890 GB", "12 GB ↑")
    with col3:
        st.metric("Model Data", "156 GB", "3 GB ↑")
    with col4:
        st.metric("Available Space", "1.2 TB", "45 GB ↓")

def show_user_management():
    """Display user management and access control"""

    st.subheader("User Management & Access Control")

    # Current user info
    st.markdown("**Current Session**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**User:** admin@company.com")
    with col2:
        st.info("**Role:** System Administrator")
    with col3:
        st.info("**Last Login:** 2 hours ago")

    st.markdown("---")

    # User management tabs
    user_tab1, user_tab2, user_tab3 = st.tabs(["Users", "Roles & Permissions", "Authentication"])

    with user_tab1:
        st.subheader("System Users")

        # Add new user
        with st.expander("Add New User"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username")
                new_email = st.text_input("Email Address")
                new_role = st.selectbox("Role", ["Analyst", "Administrator", "Viewer", "Manager"])
            with col2:
                new_department = st.text_input("Department")
                send_invitation = st.checkbox("Send Email Invitation", value=True)
                temporary_password = st.text_input("Temporary Password", type="password")

            if st.button("Add User"):
                st.success(f"User {new_username} added successfully!")

        # Existing users table
        users_data = [
            {"Username": "admin", "Email": "admin@company.com", "Role": "Administrator",
             "Status": "Active", "Last Login": "2 hours ago"},
            {"Username": "alice.smith", "Email": "alice@company.com", "Role": "Analyst",
             "Status": "Active", "Last Login": "1 day ago"},
            {"Username": "bob.jones", "Email": "bob@company.com", "Role": "Manager",
             "Status": "Active", "Last Login": "3 days ago"},
            {"Username": "charlie.brown", "Email": "charlie@company.com", "Role": "Viewer",
             "Status": "Inactive", "Last Login": "2 weeks ago"}
        ]

        import pandas as pd
        users_df = pd.DataFrame(users_data)

        # Display users with action buttons
        for idx, user in users_df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                status_color = "🟢" if user['Status'] == 'Active' else "🔴"
                st.write(f"{status_color} **{user['Username']}** ({user['Role']})")
                st.caption(f"{user['Email']} • Last: {user['Last Login']}")
            with col2:
                st.write("")  # Spacer
            with col3:
                if st.button("Edit", key=f"edit_{idx}"):
                    st.info(f"Edit user: {user['Username']}")
            with col4:
                if st.button("Delete", key=f"delete_{idx}"):
                    st.error(f"Delete user: {user['Username']}")

    with user_tab2:
        st.subheader("Roles & Permissions")

        # Role definitions
        roles_permissions = {
            "Administrator": ["Full System Access", "User Management", "System Configuration",
                           "Data Management", "Model Management"],
            "Manager": ["View All Alerts", "Assign Investigations", "Generate Reports",
                       "View Analytics", "User Oversight"],
            "Analyst": ["View Alerts", "Investigate Incidents", "Update Alert Status",
                       "View Network Data", "Basic Analytics"],
            "Viewer": ["View Dashboards", "View Reports", "Read-only Access"]
        }

        selected_role = st.selectbox("Select Role to View/Edit", list(roles_permissions.keys()))

        st.markdown(f"**Permissions for {selected_role}:**")

        all_permissions = [
            "View Dashboard", "View Alerts", "Create Alerts", "Update Alerts", "Delete Alerts",
            "View Network Data", "Export Data", "Import Data", "View Analytics", "Generate Reports",
            "Model Management", "System Configuration", "User Management", "Backup/Restore"
        ]

        current_permissions = roles_permissions.get(selected_role, [])

        updated_permissions = []
        for permission in all_permissions:
            is_granted = st.checkbox(
                permission,
                value=any(perm in permission for perm in current_permissions),
                key=f"perm_{selected_role}_{permission}"
            )
            if is_granted:
                updated_permissions.append(permission)

        if st.button("Update Permissions"):
            st.success(f"Permissions updated for {selected_role} role!")

    with user_tab3:
        st.subheader("Authentication Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Password Policy**")
            min_password_length = st.number_input("Minimum Password Length", 6, 20, 8)
            require_uppercase = st.checkbox("Require Uppercase Letters", value=True)
            require_lowercase = st.checkbox("Require Lowercase Letters", value=True)
            require_numbers = st.checkbox("Require Numbers", value=True)
            require_symbols = st.checkbox("Require Special Characters", value=True)
            password_expiry = st.number_input("Password Expiry (days)", 30, 365, 90)

            st.markdown("**Session Settings**")
            session_timeout = st.number_input("Session Timeout (minutes)", 15, 480, 120)
            max_concurrent_sessions = st.number_input("Max Concurrent Sessions", 1, 10, 3)

        with col2:
            st.markdown("**Multi-Factor Authentication**")
            enable_mfa = st.checkbox("Enable MFA", value=True)
            if enable_mfa:
                mfa_methods = st.multiselect("Supported MFA Methods",
                                           ["TOTP (Google Authenticator)", "SMS", "Email", "Hardware Token"],
                                           default=["TOTP (Google Authenticator)", "Email"])

            st.markdown("**Single Sign-On (SSO)**")
            enable_sso = st.checkbox("Enable SSO Integration", value=False)
            if enable_sso:
                sso_provider = st.selectbox("SSO Provider", ["Active Directory", "LDAP", "SAML", "OAuth2"])
                sso_endpoint = st.text_input("SSO Endpoint URL")

        if st.button("Save Authentication Settings"):
            st.success("Authentication settings saved successfully!")

def show_system_maintenance():
    """Display system maintenance and monitoring"""

    st.subheader("System Maintenance & Monitoring")

    # System status
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("System Uptime", "15d 4h 23m", "")
    with col2:
        st.metric("CPU Usage", "45%", "-5%")
    with col3:
        st.metric("Memory Usage", "2.1GB / 8GB", "+0.2GB")
    with col4:
        st.metric("Disk Usage", "65%", "+2%")

    st.markdown("---")

    # Maintenance tabs
    maint_tab1, maint_tab2, maint_tab3, maint_tab4 = st.tabs([
        "System Health", "Scheduled Tasks", "Logs", "Updates"
    ])

    with maint_tab1:
        st.subheader("System Health Monitoring")

        # Health checks
        health_checks = [
            {"Component": "Detection Engine", "Status": "Healthy", "Last Check": "2 min ago"},
            {"Component": "Database", "Status": "Healthy", "Last Check": "1 min ago"},
            {"Component": "Web Interface", "Status": "Healthy", "Last Check": "30 sec ago"},
            {"Component": "Alert System", "Status": "Warning", "Last Check": "5 min ago"},
            {"Component": "Data Pipeline", "Status": "Healthy", "Last Check": "1 min ago"},
            {"Component": "Model Training", "Status": "Healthy", "Last Check": "10 min ago"}
        ]

        for check in health_checks:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                status_emoji = {"Healthy": "✅", "Warning": "⚠️", "Error": "❌"}
                st.write(f"{status_emoji[check['Status']]} **{check['Component']}**")
            with col2:
                st.write(check['Status'])
            with col3:
                st.caption(check['Last Check'])

        # Resource monitoring
        st.subheader("Resource Usage Trends")

        import plotly.graph_objects as go
        import numpy as np

        hours = list(range(24))
        cpu_usage = [30 + 15 * np.sin(h/4) + np.random.normal(0, 3) for h in hours]
        memory_usage = [40 + 10 * np.sin((h+6)/4) + np.random.normal(0, 2) for h in hours]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hours, y=cpu_usage, mode='lines', name='CPU %'))
        fig.add_trace(go.Scatter(x=hours, y=memory_usage, mode='lines', name='Memory %'))

        fig.update_layout(
            title="System Resource Usage (Last 24 Hours)",
            xaxis_title="Hour",
            yaxis_title="Usage (%)"
        )
        st.plotly_chart(fig, width='stretch')

    with maint_tab2:
        st.subheader("Scheduled Tasks & Jobs")

        # Add new scheduled task
        with st.expander("Add New Scheduled Task"):
            task_name = st.text_input("Task Name")
            task_type = st.selectbox("Task Type", [
                "Model Training", "Data Cleanup", "Database Backup",
                "Report Generation", "System Maintenance"
            ])
            schedule_type = st.selectbox("Schedule", ["Daily", "Weekly", "Monthly", "Custom Cron"])
            if schedule_type == "Custom Cron":
                cron_expression = st.text_input("Cron Expression", placeholder="0 2 * * *")

            task_enabled = st.checkbox("Task Enabled", value=True)

            if st.button("Add Scheduled Task"):
                st.success(f"Scheduled task '{task_name}' added successfully!")

        # Existing scheduled tasks
        scheduled_tasks = [
            {"Name": "Nightly Model Retrain", "Type": "Model Training", "Schedule": "Daily at 2:00 AM",
             "Status": "Active", "Last Run": "Success (6h ago)", "Next Run": "18h"},
            {"Name": "Weekly Data Cleanup", "Type": "Data Cleanup", "Schedule": "Weekly (Sunday)",
             "Status": "Active", "Last Run": "Success (2d ago)", "Next Run": "5d"},
            {"Name": "Database Backup", "Type": "Database Backup", "Schedule": "Daily at 1:00 AM",
             "Status": "Active", "Last Run": "Success (7h ago)", "Next Run": "17h"},
            {"Name": "Monthly Report", "Type": "Report Generation", "Schedule": "Monthly (1st)",
             "Status": "Inactive", "Last Run": "Failed (1mo ago)", "Next Run": "N/A"}
        ]

        for task in scheduled_tasks:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    status_color = {"Active": "🟢", "Inactive": "🔴"}
                    st.write(f"{status_color[task['Status']]} **{task['Name']}**")
                    st.caption(f"{task['Schedule']} • {task['Type']}")
                with col2:
                    st.write(task['Last Run'])
                with col3:
                    st.write(f"Next: {task['Next Run']}")
                with col4:
                    if st.button("Run Now", key=f"run_{task['Name']}"):
                        st.info(f"Running {task['Name']}...")

    with maint_tab3:
        st.subheader("System Logs")

        # Log filtering
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            log_level = st.selectbox("Log Level", ["All", "ERROR", "WARNING", "INFO", "DEBUG"])
        with col2:
            log_component = st.selectbox("Component", ["All", "Detection", "Database", "Web", "Auth"])
        with col3:
            log_time_range = st.selectbox("Time Range", ["Last Hour", "Last 24h", "Last 7d"])
        with col4:
            if st.button("🔄 Refresh Logs"):
                st.rerun()

        # Sample log entries
        log_entries = [
            {"Timestamp": "2024-01-15 14:30:45", "Level": "INFO", "Component": "Detection",
             "Message": "Model inference completed successfully"},
            {"Timestamp": "2024-01-15 14:30:42", "Level": "WARNING", "Component": "Database",
             "Message": "Connection pool approaching maximum capacity"},
            {"Timestamp": "2024-01-15 14:30:38", "Level": "INFO", "Component": "Web",
             "Message": "User admin@company.com logged in successfully"},
            {"Timestamp": "2024-01-15 14:30:35", "Level": "ERROR", "Component": "Detection",
             "Message": "Failed to process packet batch: timeout error"},
            {"Timestamp": "2024-01-15 14:30:30", "Level": "INFO", "Component": "Auth",
             "Message": "MFA verification successful for user alice@company.com"}
        ]

        for entry in log_entries:
            level_colors = {"ERROR": "🔴", "WARNING": "⚠️", "INFO": "ℹ️", "DEBUG": "🔍"}
            st.markdown(f"""
            {level_colors[entry['Level']]} **{entry['Timestamp']}** | {entry['Component']} | {entry['Level']}  
            {entry['Message']}
            """)
            st.markdown("---")

    with maint_tab4:
        st.subheader("System Updates")

        # Current version info
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Current System Information**")
            st.info("""
            **NIDS Version:** 2.1.3  
            **Build:** 20240115-1430  
            **Last Updated:** 5 days ago  
            **Python:** 3.11.7  
            **TensorFlow:** 2.15.0  
            """)

            if st.button("🔍 Check for Updates"):
                st.success("System is up to date!")

        with col2:
            st.markdown("**Update Settings**")

            auto_updates = st.checkbox("Enable Automatic Updates", value=False)
            if auto_updates:
                update_schedule = st.selectbox("Update Schedule",
                                             ["Daily", "Weekly", "Monthly"])
                maintenance_window = st.time_input("Maintenance Window Start")

            update_notifications = st.checkbox("Update Notifications", value=True)
            include_beta = st.checkbox("Include Beta Releases", value=False)

            if st.button("Save Update Settings"):
                st.success("Update settings saved!")

        # Update history
        st.subheader("Update History")

        update_history = [
            {"Version": "2.1.3", "Date": "2024-01-10", "Type": "Security Update",
             "Status": "Installed", "Notes": "Fixed adversarial detection bug"},
            {"Version": "2.1.2", "Date": "2024-01-05", "Type": "Feature Update",
             "Status": "Installed", "Notes": "Added new ML features"},
            {"Version": "2.1.1", "Date": "2023-12-20", "Type": "Bug Fix",
             "Status": "Installed", "Notes": "Performance improvements"},
            {"Version": "2.1.0", "Date": "2023-12-15", "Type": "Major Release",
             "Status": "Installed", "Notes": "New detection algorithms"}
        ]

        import pandas as pd
        history_df = pd.DataFrame(update_history)
        st.dataframe(history_df, width='stretch', hide_index=True)

    # Emergency controls
    st.markdown("---")
    st.subheader("🚨 Emergency Controls")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🛑 Emergency Stop", type="secondary"):
            st.error("Emergency stop initiated - All detection services stopped")

    with col2:
        if st.button("🔄 Restart Services", type="secondary"):
            st.warning("Restarting all NIDS services...")

    with col3:
        if st.button("📋 Generate System Report", type="primary"):
            st.success("System diagnostic report generated")


if __name__ == "__main__":
    show()