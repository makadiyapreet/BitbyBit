# notification_system.py

"""
Multi-Channel Notification System
Sends SMS, Email, and Push notifications for coastal threat alerts
Integrates seamlessly with your existing main.py
"""

import json
import logging
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List
import time

from rich import print as rprint
from rich.json import JSON

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationSystem:
    def __init__(self):
        """Initialize notification system with Indian emergency contacts"""
        
        # SMS Configuration (Twilio - Sign up free at twilio.com)
        self.twilio_enabled = False
        try:
            from twilio.rest import Client
            # Add your Twilio credentials here (free trial available)
            self.twilio_account_sid = "your_twilio_account_sid"
            self.twilio_auth_token = "your_twilio_auth_token"
            self.twilio_phone = "+1234567890"  # Your Twilio phone number
            
            if self.twilio_account_sid != "your_twilio_account_sid":
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
                self.twilio_enabled = True
                logger.info("📱 Twilio SMS enabled")
        except ImportError:
            logger.info("📱 Twilio not installed - SMS disabled (pip install twilio)")
        except Exception as e:
            logger.info(f"📱 Twilio disabled: {e}")
        
        # Email Configuration (Gmail SMTP)
        self.email_enabled = False
        try:
            # Add your Gmail app password here (generate at myaccount.google.com)
            self.email_sender = "your_email@gmail.com"
            self.email_password = "your_app_password"  # Gmail app password
            
            if self.email_sender != "your_email@gmail.com":
                self.email_enabled = True
                logger.info("📧 Email notifications enabled")
        except:
            logger.info("📧 Email disabled - configure Gmail credentials")
        
        # Indian Coastal Emergency Contacts
        self.emergency_contacts = {
            'SMS': [
                '+91-9999999999',  # NDMA Control Room
                '+91-8888888888',  # Coast Guard Emergency
                '+91-7777777777',  # Local Disaster Management
            ],
            'EMAIL': [
                'ndma.emergency@gov.in',
                'coastguard.ops@indiannavy.gov.in',
                'disaster.mgmt@maharashtra.gov.in',
                'emergency.response@kerala.gov.in',
                'coastal.alert@gujarat.gov.in',
                'marine.safety@odisha.gov.in'
            ],
            'STAKEHOLDERS': {
                'Disaster Management': ['+91-9999999991', 'disaster@ndma.gov.in'],
                'Coast Guard': ['+91-9999999992', 'ops@coastguard.gov.in'],
                'Environmental NGOs': ['+91-9999999993', 'alerts@cpreec.org'],
                'Fishing Communities': ['+91-9999999994', 'fisher@community.org'],
                'Port Authorities': ['+91-9999999995', 'port.ops@gov.in']
            }
        }
        
        # Notification templates
        self.templates = {
            'SMS': "🚨 COASTAL ALERT\n{threat_type} at {location}\nSeverity: {severity:.1f}/1.0\nTime: {time}\nAction: {action}",
            'EMAIL_SUBJECT': "🚨 URGENT: {threat_type} Alert - {location}",
            'EMAIL_BODY': """
            <html><body>
            <h2 style="color: red;">🚨 COASTAL THREAT ALERT</h2>
            <p><strong>Location:</strong> {location}</p>
            <p><strong>Threat Type:</strong> {threat_type}</p>
            <p><strong>Severity Score:</strong> {severity:.2f}/1.0</p>
            <p><strong>Confidence:</strong> {confidence:.0%}</p>
            <p><strong>Time:</strong> {time}</p>
            <p><strong>Priority:</strong> {priority}</p>
            
            <h3>Immediate Actions Required:</h3>
            <ul>
            {action_list}
            </ul>
            
            <h3>Data Snapshot:</h3>
            <ul>
            <li>Tide Level: {tide_level:.2f}m</li>
            <li>Wind Speed: {wind_speed:.1f} km/h</li>
            <li>Pressure: {pressure:.1f} hPa</li>
            <li>Pollution Index: {pollution:.2f}</li>
            </ul>
            
            <p><strong>Estimated Impact:</strong> {impact}</p>
            
            <p style="color: red;"><strong>This is an automated alert from the Coastal Threat Monitoring System</strong></p>
            </body></html>
            """
        }
        
        logger.info("🔔 Notification system initialized")

    def send_sms_alert(self, alert: Dict, recipients: List[str] = None):
        """Send SMS alerts to specified recipients"""
        if not self.twilio_enabled:
            logger.info("📱 SMS simulation mode (Twilio not configured)")
            self._simulate_sms(alert, recipients or self.emergency_contacts['SMS'])
            return
        
        try:
            recipients = recipients or self.emergency_contacts['SMS']
            
            # Format SMS message
            message_text = self.templates['SMS'].format(
                threat_type=alert['threat_type'],
                location=alert['location'],
                severity=alert['severity_score'],
                time=datetime.now().strftime('%H:%M'),
                action=alert['recommendations'][0][:50] if alert['recommendations'] else 'Monitor situation'
            )
            
            successful_sends = 0
            for phone_number in recipients:
                try:
                    message = self.twilio_client.messages.create(
                        body=message_text,
                        from_=self.twilio_phone,
                        to=phone_number
                    )
                    successful_sends += 1
                    logger.info(f"📱 SMS sent to {phone_number}: {message.sid}")
                except Exception as e:
                    logger.error(f"❌ SMS failed to {phone_number}: {e}")
            
            logger.info(f"📱 SMS alerts: {successful_sends}/{len(recipients)} successful")
            
        except Exception as e:
            logger.error(f"❌ SMS system error: {e}")
            self._simulate_sms(alert, recipients or self.emergency_contacts['SMS'])

    def send_email_alert(self, alert: Dict, recipients: List[str] = None):
        """Send email alerts to specified recipients"""
        if not self.email_enabled:
            logger.info("📧 Email simulation mode (Gmail not configured)")
            self._simulate_email(alert, recipients or self.emergency_contacts['EMAIL'])
            return
        
        try:
            recipients = recipients or self.emergency_contacts['EMAIL']
            
            # Format email content
            subject = self.templates['EMAIL_SUBJECT'].format(
                threat_type=alert['threat_type'],
                location=alert['location']
            )
            
            action_list = ''.join([f"<li>{action}</li>" for action in alert['recommendations']])
            
            body_html = self.templates['EMAIL_BODY'].format(
                location=alert['location'],
                threat_type=alert['threat_type'],
                severity=alert['severity_score'],
                confidence=alert['confidence'],
                time=alert['timestamp'],
                priority=alert['response_priority'],
                action_list=action_list,
                tide_level=alert['data_snapshot']['tide_level'],
                wind_speed=alert['data_snapshot']['wind_speed'],
                pressure=alert['data_snapshot']['pressure'],
                pollution=alert['data_snapshot']['pollution_index'],
                impact=alert['estimated_impact']
            )
            
            # Send emails
            successful_sends = 0
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                
                for recipient in recipients:
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = self.email_sender
                        msg['To'] = recipient
                        msg['Subject'] = subject
                        msg.attach(MIMEText(body_html, 'html'))
                        
                        server.send_message(msg)
                        successful_sends += 1
                        logger.info(f"📧 Email sent to {recipient}")
                    except Exception as e:
                        logger.error(f"❌ Email failed to {recipient}: {e}")
            
            logger.info(f"📧 Email alerts: {successful_sends}/{len(recipients)} successful")
            
        except Exception as e:
            logger.error(f"❌ Email system error: {e}")
            self._simulate_email(alert, recipients or self.emergency_contacts['EMAIL'])

    def send_push_notification(self, alert: Dict, registration_ids: List[str] = None):
        """Send push notifications (simulated - requires FCM setup)"""
        logger.info("📲 Push notification simulation mode")
        
        apps = ['Coastal Alert App', 'Emergency Response App', 'Fisher Safety App']
        
        push_data = {
            'title': f"🚨 {alert['threat_type']} at {alert['location']}",
            'body': f"Severity: {alert['severity_score']:.1f}/1.0 - {alert['recommendations'][0][:50] if alert['recommendations'] else 'Take caution'}",
            'data': {
                'alert_id': alert['id'],
                'location': alert['location'],
                'severity': alert['severity_score'],
                'timestamp': alert['timestamp']
            }
        }
        
        for app in apps:
            logger.info(f"📲 Push sent to {app}: {push_data['title']}")
        
        logger.info(f"📲 Push notifications sent to {len(apps)} mobile apps")

    def broadcast_to_stakeholders(self, alert: Dict):
        """Send targeted alerts to different stakeholder groups"""
        logger.info("🎯 Broadcasting to stakeholder groups...")
        
        for stakeholder_type, contacts in self.emergency_contacts['STAKEHOLDERS'].items():
            phone, email = contacts
            
            # Customize message based on stakeholder
            custom_alert = self._customize_for_stakeholder(alert, stakeholder_type)
            
            logger.info(f"👥 Alerting {stakeholder_type}: {phone}, {email}")
            
            # Send SMS and Email (or simulate)
            if self.twilio_enabled:
                self.send_sms_alert(custom_alert, [phone])
            else:
                logger.info(f"📱 SMS to {stakeholder_type}: {phone} - {custom_alert['threat_type']}")
            
            if self.email_enabled:
                self.send_email_alert(custom_alert, [email])
            else:
                logger.info(f"📧 Email to {stakeholder_type}: {email} - {custom_alert['threat_type']}")

    def dispatch_alert(self, alert: Dict):
        """Main method to dispatch alerts through all channels"""
        start_time = time.time()
        
        # Structured JSON log entry
        log_str = json.dumps({
        "timestamp": str(datetime.now()),
        "alert_id": alert.get("id"),
        "location": alert.get("location"),
        "threat_type": alert.get("threat_type"),
        "severity": alert.get("severity_score"),
        "channels": ["sms", "email", "push", "stakeholders"]
    })

        logger.info(JSON(log_str))

        # Colorized console summary
        severity = alert["severity_score"]
        color = "red" if severity > 0.7 else "yellow" if severity > 0.4 else "green"
        rprint(f"[bold {color}]🚨 {alert['threat_type'].upper()}[/] at [underline]{alert['location']}[/]  Severity: [bold {color}]{severity:.2f}[/]")

        # Batch suppression: skip notifications for low-severity alerts
        if severity < 0.4:
            rprint(f"[dim]ℹ️ Suppressed low-severity alert at {alert['location']}[/]")
            return
        
        # Create threads for concurrent notification sending
        threads = []
        
        # SMS Thread
        sms_thread = threading.Thread(
            target=self.send_sms_alert,
            args=(alert,),
            name="SMS_Alert"
        )
        threads.append(sms_thread)
        
        # Email Thread
        email_thread = threading.Thread(
            target=self.send_email_alert,
            args=(alert,),
            name="Email_Alert"
        )
        threads.append(email_thread)
        
        # Push Notification Thread
        push_thread = threading.Thread(
            target=self.send_push_notification,
            args=(alert,),
            name="Push_Alert"
        )
        threads.append(push_thread)
        
        # Stakeholder Broadcast Thread
        stakeholder_thread = threading.Thread(
            target=self.broadcast_to_stakeholders,
            args=(alert,),
            name="Stakeholder_Broadcast"
        )
        threads.append(stakeholder_thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout per thread
        
        processing_time = time.time() - start_time
        
        logger.info(f"✅ Multi-channel alert dispatch completed in {processing_time:.2f} seconds")
        
        # Log alert dispatch
        self._log_alert_dispatch(alert, processing_time)

    def _customize_for_stakeholder(self, alert: Dict, stakeholder_type: str) -> Dict:
        """Customize alert message for specific stakeholder"""
        custom_alert = alert.copy()
        
        stakeholder_actions = {
            'Disaster Management': [
                "Deploy emergency response teams immediately",
                "Activate evacuation protocols for affected areas",
                "Coordinate with local authorities"
            ],
            'Coast Guard': [
                "Issue maritime safety warning",
                "Deploy rescue vessels to high-risk areas",
                "Monitor vessel traffic in affected zones"
            ],
            'Environmental NGOs': [
                "Document environmental impact",
                "Prepare cleanup and recovery operations",
                "Monitor wildlife and marine ecosystem"
            ],
            'Fishing Communities': [
                "Return vessels to shore immediately",
                "Secure fishing equipment and boats",
                "Move to higher ground if necessary"
            ],
            'Port Authorities': [
                "Halt port operations if necessary",
                "Secure all vessels and equipment",
                "Issue navigation warnings"
            ]
        }
        
        # Add stakeholder-specific recommendations
        if stakeholder_type in stakeholder_actions:
            custom_alert['recommendations'] = stakeholder_actions[stakeholder_type] + alert['recommendations']
        
        return custom_alert

    def _simulate_sms(self, alert: Dict, recipients: List[str]):
        """Simulate SMS sending when Twilio not configured"""
        message = self.templates['SMS'].format(
            threat_type=alert['threat_type'],
            location=alert['location'],
            severity=alert['severity_score'],
            time=datetime.now().strftime('%H:%M'),
            action=alert['recommendations'][0][:50] if alert['recommendations'] else 'Monitor situation'
        )
        
        logger.info("📱 SMS SIMULATION:")
        for recipient in recipients:
            logger.info(f"  → {recipient}: {message[:60]}...")

    def _simulate_email(self, alert: Dict, recipients: List[str]):
        """Simulate email sending when Gmail not configured"""
        subject = self.templates['EMAIL_SUBJECT'].format(
            threat_type=alert['threat_type'],
            location=alert['location']
        )
        
        logger.info("📧 EMAIL SIMULATION:")
        for recipient in recipients:
            logger.info(f"  → {recipient}: {subject}")

    def _log_alert_dispatch(self, alert: Dict, processing_time: float):
        """Log alert dispatch for analytics"""
        log_entry = {
            'alert_id': alert['id'],
            'location': alert['location'],
            'threat_type': alert['threat_type'],
            'severity': alert['severity_score'],
            'dispatch_time': datetime.now().isoformat(),
            'processing_time': processing_time,
            'channels_used': ['SMS', 'EMAIL', 'PUSH', 'STAKEHOLDERS']
        }
        
        # Save to log file for analysis
        try:
            with open('notification_log.json', 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except:
            pass  # Don't fail if logging fails

    def get_notification_status(self) -> Dict:
        """Get current notification system status"""
        return {
            'sms_enabled': self.twilio_enabled,
            'email_enabled': self.email_enabled,
            'emergency_contacts': len(self.emergency_contacts['SMS']) + len(self.emergency_contacts['EMAIL']),
            'stakeholder_groups': len(self.emergency_contacts['STAKEHOLDERS']),
            'system_status': 'operational'
        }

    def test_notifications(self):
        """Test all notification channels with a sample alert"""
        logger.info("🧪 Testing notification system...")
        
        test_alert = {
            'id': 999,
            'location': 'Mumbai Test',
            'threat_type': 'SYSTEM_TEST',
            'severity_score': 0.5,
            'confidence': 0.9,
            'timestamp': datetime.now().isoformat(),
            'response_priority': 'TEST',
            'recommendations': ['This is a system test', 'All systems operational'],
            'estimated_impact': 'Testing notification channels',
            'data_snapshot': {
                'tide_level': 2.5,
                'wind_speed': 15.0,
                'pressure': 1013.0,
                'pollution_index': 0.1
            }
        }
        
        self.dispatch_alert(test_alert)
        logger.info("✅ Notification system test completed")

# Quick test when run directly
if __name__ == "__main__":
    print("🔔 Initializing Coastal Notification System...")
    
    notifier = NotificationSystem()
    
    # Display configuration status
    status = notifier.get_notification_status()
    print(f"📱 SMS Enabled: {status['sms_enabled']}")
    print(f"📧 Email Enabled: {status['email_enabled']}")
    print(f"👥 Emergency Contacts: {status['emergency_contacts']}")
    print(f"🎯 Stakeholder Groups: {status['stakeholder_groups']}")
    
    # Test the system
    choice = input("\nRun notification test? (y/n): ").lower()
    if choice == 'y':
        notifier.test_notifications()
    
    print("✅ Notification system ready for integration!")    
