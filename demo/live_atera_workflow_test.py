#!/usr/bin/env python3
"""
Live Atera Ticket Workflow Test
Comprehensive test simulating real ticket workflow with full user-AI interaction
30-minute timeout per ticket, complete conversation simulation
"""

import sys
import os
import asyncio
import time
import json
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_workflow_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveAteraWorkflowTest:
    """Live Atera workflow test with full conversation simulation"""

    def __init__(self):
        self.atera_api_key = os.getenv('ATERA_API_KEY')
        self.atera_base_url = os.getenv('ATERA_BASE_URL', 'https://app.atera.com/api/v3')
        self.lmstudio_url = os.getenv('LMSTUDIO_URL', 'http://127.0.0.1:1234/v1')
        self.ticket_timeout = 30 * 60  # 30 minutes in seconds
        self.conversation_history = []
        self.test_start_time = None

        # Validate credentials
        if not self.atera_api_key or self.atera_api_key == 'YOUR_ATERA_API_KEY_HERE':
            raise ValueError("ATERA_API_KEY not configured")

    def log_conversation(self, speaker, message, ticket_id=None):
        """Log conversation with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "speaker": speaker,
            "message": message,
            "ticket_id": ticket_id
        }
        self.conversation_history.append(log_entry)

        # Print to console with formatting
        if speaker == "SYSTEM":
            print(f"\n[{timestamp}] === {message} ===")
        elif speaker == "USER":
            print(f"[{timestamp}] USER: {message}")
        elif speaker == "AI":
            print(f"[{timestamp}] AI: {message}")
        elif speaker == "ATERA":
            print(f"[{timestamp}] ATERA: {message}")
        else:
            print(f"[{timestamp}] {speaker}: {message}")

    def make_atera_request(self, endpoint, method='GET', data=None):
        """Make authenticated request to Atera API"""
        headers = {
            'X-API-KEY': self.atera_api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        url = f"{self.atera_base_url}/{endpoint}"

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Atera API request failed: {e}")
            return None

    def get_live_tickets(self, limit=5):
        """Get real tickets from Atera"""
        self.log_conversation("SYSTEM", "Fetching live tickets from Atera...")

        tickets = self.make_atera_request(f"tickets?itemsInPage={limit}")

        if tickets and 'items' in tickets:
            self.log_conversation("ATERA", f"Retrieved {len(tickets['items'])} live tickets")
            return tickets['items']
        else:
            self.log_conversation("ATERA", "No tickets retrieved or API error")
            return []

    def get_ticket_details(self, ticket_id):
        """Get detailed ticket information"""
        self.log_conversation("SYSTEM", f"Fetching details for ticket {ticket_id}")

        ticket = self.make_atera_request(f"tickets/{ticket_id}")

        if ticket:
            self.log_conversation("ATERA", f"Retrieved ticket details: {ticket.get('TicketTitle', 'Unknown Title')}")
            return ticket
        else:
            self.log_conversation("ATERA", f"Failed to retrieve ticket {ticket_id}")
            return None

    def update_ticket_comment(self, ticket_id, comment):
        """Add comment to ticket"""
        self.log_conversation("SYSTEM", f"Adding comment to ticket {ticket_id}")

        comment_data = {
            "TicketID": ticket_id,
            "Comment": comment,
            "IsInternal": False,
            "CommentType": "Resolution"
        }

        # Note: Commenting out actual comment posting due to API permissions
        # This focuses on conversation simulation as requested
        # result = self.make_atera_request(f"tickets/{ticket_id}/comments", method='POST', data=comment_data)

        # Simulate successful comment addition for testing purposes
        self.log_conversation("ATERA", f"[SIMULATED] Comment added to ticket {ticket_id}: {comment}")
        return True

    def simulate_ai_response(self, ticket_info, user_message=None):
        """Simulate AI response using LM Studio or simple logic"""
        self.log_conversation("SYSTEM", "AI processing ticket information...")

        # Try LM Studio first
        ai_response = self.get_lmstudio_response(ticket_info, user_message)

        if not ai_response:
            # Fallback to rule-based response
            ai_response = self.get_fallback_ai_response(ticket_info, user_message)

        return ai_response

    def get_lmstudio_response(self, ticket_info, user_message=None):
        """Get response from LM Studio"""
        try:
            # Construct prompt
            prompt = self.build_ai_prompt(ticket_info, user_message)

            payload = {
                "model": "local-model",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert IT support technician. Provide helpful, step-by-step solutions. Ask clarifying questions when needed. Be conversational and helpful."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.7,
                "stream": False
            }

            response = requests.post(
                f"{self.lmstudio_url}/chat/completions",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content'].strip()
                    self.log_conversation("SYSTEM", "LM Studio response received")
                    return content

        except Exception as e:
            logger.warning(f"LM Studio request failed: {e}")

        return None

    def get_fallback_ai_response(self, ticket_info, user_message=None):
        """Fallback AI response using rule-based logic"""
        title = ticket_info.get('TicketTitle', '').lower()
        description = ticket_info.get('FirstComment', '').lower()

        # Common IT issues and responses
        if 'password' in title or 'password' in description:
            if user_message and 'reset' in user_message.lower():
                return "I've initiated a password reset. You should receive an email with instructions within 5 minutes. Please check your spam folder as well. Can you confirm your email address is current in the system?"
            else:
                return "I see you're having password issues. Would you like me to reset your password, or are you having trouble with a specific application? Could you provide more details about what happens when you try to log in?"

        elif 'internet' in title or 'connection' in title or 'wifi' in title:
            if user_message and ('tried' in user_message.lower() or 'restarted' in user_message.lower()):
                return "Since you've already tried basic troubleshooting, let's check if other devices are affected. Are other computers/phones on the same network working? Also, can you see your WiFi network in the available networks list?"
            else:
                return "I can help with your connection issue. Let's start with basic troubleshooting: 1) Can you restart your computer? 2) Unplug your router for 30 seconds, then plug it back in. 3) Try connecting to WiFi again. Let me know what happens!"

        elif 'email' in title or 'outlook' in title:
            return "I'll help you with your email issue. Can you tell me: 1) What error message are you seeing? 2) Are you able to send emails, receive emails, or neither? 3) When did this issue start? This will help me provide the right solution."

        elif 'printer' in title or 'print' in title:
            if user_message and 'installed' in user_message.lower():
                return "Great that you've installed the driver. Now let's test: 1) Try printing a test page from Windows (Settings > Printers & Scanners > [Your Printer] > Print Test Page). 2) If that works, try printing from the application that was having issues. What happens?"
            else:
                return "I can help with your printer issue. First, let's check: 1) Is the printer powered on and connected to WiFi/network? 2) Do you see any error lights on the printer? 3) What happens when you try to print - any error messages? Let me know and I'll guide you through the fix."

        elif 'slow' in title or 'performance' in title:
            return "I understand your computer is running slowly. Let's diagnose this: 1) How long does it take to start up? 2) Press Ctrl+Shift+Esc to open Task Manager - what's the CPU and Memory usage? 3) When did you first notice the slowness? I'll help optimize your system performance."

        elif 'software' in title or 'application' in title or 'program' in title:
            return "I'll help you with your software issue. Can you provide these details: 1) What is the exact name of the software? 2) What error message do you see (if any)? 3) What were you trying to do when the problem occurred? 4) Does it happen every time or only sometimes?"

        else:
            # Generic response
            return f"I've reviewed your ticket about '{ticket_info.get('TicketTitle', 'your issue')}'. To provide the best help, could you give me a bit more detail about: 1) What exactly is happening? 2) What error messages do you see? 3) When did this start? I'm here to help resolve this for you!"

    def build_ai_prompt(self, ticket_info, user_message=None):
        """Build prompt for AI"""
        prompt = f"""
TICKET INFORMATION:
Title: {ticket_info.get('TicketTitle', 'No title')}
Description: {ticket_info.get('FirstComment', 'No description')}
Status: {ticket_info.get('TicketStatus', 'Unknown')}
Priority: {ticket_info.get('TicketPriority', 'Unknown')}
Created: {ticket_info.get('TicketCreatedDate', 'Unknown')}
"""

        if user_message:
            prompt += f"\n\nUSER RESPONSE: {user_message}"

        prompt += "\n\nPlease provide a helpful response as an IT support technician. Ask clarifying questions if needed."

        return prompt

    def simulate_user_responses(self, ticket_info, ai_message):
        """Simulate realistic user responses based on ticket type and AI message"""
        title = ticket_info.get('TicketTitle', '').lower()

        # User response patterns
        if 'password' in title:
            if 'confirm your email' in ai_message.lower():
                return "Yes, my email is correct - it's john.doe@company.com. I haven't received the reset email yet though."
            elif 'reset' in ai_message.lower():
                return "Yes please reset it. I think I changed it recently and can't remember the new one."
            else:
                return "I can't log into my computer this morning. It keeps saying invalid password but I'm sure I'm typing it correctly."

        elif 'connection' in title or 'internet' in title or 'wifi' in title:
            if 'other devices' in ai_message.lower():
                return "My phone works fine on the same WiFi, but my laptop won't connect. It shows the network but says 'Can't connect to this network'."
            elif 'restart' in ai_message.lower():
                return "I tried restarting already but it didn't help. The WiFi icon shows networks but mine has an exclamation mark next to it."
            else:
                return "The internet was working fine yesterday but today I can't get online at all. My WiFi shows connected but no websites load."

        elif 'email' in title:
            if 'error message' in ai_message.lower():
                return "It says 'Cannot connect to server' when I try to send emails. I can receive emails fine though. Started this morning."
            else:
                return "Outlook keeps asking for my password even though I enter it correctly. It worked fine last week."

        elif 'printer' in title:
            if 'test page' in ai_message.lower():
                return "The test page printed fine! But when I try to print from Word it still says 'printer offline'. This is confusing."
            elif 'error lights' in ai_message.lower():
                return "There's a red light blinking on the printer. I tried turning it off and on but the light is still there."
            else:
                return "I'm trying to print a document but it says 'printer not found'. It was working yesterday though."

        elif 'slow' in title:
            if 'task manager' in ai_message.lower():
                return "CPU shows 85% and Memory is at 92%. There's something called 'Service Host' using a lot. Computer takes about 5 minutes to start up now."
            else:
                return "Everything is really slow - opening programs takes forever and clicking anything has a long delay. Started about a week ago."

        else:
            # Generic user responses
            responses = [
                "I tried that but it didn't work. What else can I try?",
                "That helped a little but the problem is still there. Any other ideas?",
                "I'm not very technical - could you walk me through that step by step?",
                "It's still not working. Should I restart my computer?",
                "The error message now says something different. What does that mean?"
            ]
            import random
            return random.choice(responses)

    async def run_full_ticket_conversation(self, ticket):
        """Run complete conversation flow for a ticket with 30-minute timeout"""
        ticket_id = ticket.get('TicketID')
        ticket_title = ticket.get('TicketTitle', 'Unknown Issue')

        self.log_conversation("SYSTEM", f"Starting full conversation test for Ticket #{ticket_id}: {ticket_title}")

        start_time = time.time()
        conversation_rounds = 0
        max_rounds = 8  # Limit conversation rounds

        # Get detailed ticket information
        detailed_ticket = self.get_ticket_details(ticket_id)
        if not detailed_ticket:
            self.log_conversation("SYSTEM", "Failed to get ticket details, aborting conversation")
            return False

        # Initial AI response to ticket
        self.log_conversation("AI", "Hello! I've reviewed your ticket and I'm here to help resolve this issue.")
        initial_ai_response = self.simulate_ai_response(detailed_ticket)
        self.log_conversation("AI", initial_ai_response)

        # Add initial comment to ticket
        comment = f"TicketZero AI: {initial_ai_response}"
        self.update_ticket_comment(ticket_id, comment)

        conversation_rounds += 1

        # Continue conversation
        current_ai_message = initial_ai_response

        while conversation_rounds < max_rounds:
            elapsed_time = time.time() - start_time

            # Check 30-minute timeout
            if elapsed_time > self.ticket_timeout:
                self.log_conversation("SYSTEM", f"TIMEOUT: 30-minute limit reached for ticket {ticket_id}")
                timeout_message = "This ticket has been open for 30 minutes. I'm escalating to a senior technician for further assistance. A team member will contact you shortly."
                self.log_conversation("AI", timeout_message)
                self.update_ticket_comment(ticket_id, f"TicketZero AI - ESCALATED: {timeout_message}")
                break

            # Simulate user response (realistic timing)
            await asyncio.sleep(2)  # User thinking time

            user_response = self.simulate_user_responses(detailed_ticket, current_ai_message)
            self.log_conversation("USER", user_response)

            # Add user response as internal comment
            user_comment = f"Simulated User Response: {user_response}"
            self.update_ticket_comment(ticket_id, user_comment)

            # AI processing time
            await asyncio.sleep(3)

            # Generate AI response
            ai_response = self.simulate_ai_response(detailed_ticket, user_response)
            self.log_conversation("AI", ai_response)

            # Add AI response to ticket
            ai_comment = f"TicketZero AI: {ai_response}"
            self.update_ticket_comment(ticket_id, ai_comment)

            current_ai_message = ai_response
            conversation_rounds += 1

            # Check for resolution indicators
            if any(word in ai_response.lower() for word in ['resolved', 'fixed', 'working', 'solved']):
                self.log_conversation("AI", "Great! It looks like we've resolved your issue. I'm marking this ticket as resolved. Please let us know if you need any further assistance!")
                resolution_comment = "TicketZero AI - RESOLVED: Issue has been successfully resolved through automated assistance."
                self.update_ticket_comment(ticket_id, resolution_comment)
                break

            # Small delay between rounds
            await asyncio.sleep(1)

        total_time = time.time() - start_time
        self.log_conversation("SYSTEM", f"Conversation completed for ticket {ticket_id}. Duration: {total_time:.1f} seconds, Rounds: {conversation_rounds}")

        return True

    async def run_comprehensive_test(self):
        """Run comprehensive live workflow test"""
        self.test_start_time = time.time()

        self.log_conversation("SYSTEM", "STARTING COMPREHENSIVE LIVE ATERA WORKFLOW TEST")
        self.log_conversation("SYSTEM", f"Test Configuration: 30-minute timeout per ticket, Full conversation simulation")
        self.log_conversation("SYSTEM", f"Atera API: {self.atera_base_url}")
        self.log_conversation("SYSTEM", f"LM Studio: {self.lmstudio_url}")

        # Test Atera connectivity
        self.log_conversation("SYSTEM", "Testing Atera API connectivity...")
        test_response = self.make_atera_request("tickets?itemsInPage=1")
        if not test_response:
            self.log_conversation("SYSTEM", "CRITICAL: Cannot connect to Atera API")
            return False

        self.log_conversation("SYSTEM", "Atera API connection successful")

        # Get live tickets
        tickets = self.get_live_tickets(3)  # Test with 3 tickets max

        if not tickets:
            self.log_conversation("SYSTEM", "No tickets available for testing")
            return False

        self.log_conversation("SYSTEM", f"Found {len(tickets)} tickets for testing")

        # Process each ticket
        successful_tests = 0
        for i, ticket in enumerate(tickets):
            self.log_conversation("SYSTEM", f"=== TESTING TICKET {i+1} OF {len(tickets)} ===")

            try:
                success = await self.run_full_ticket_conversation(ticket)
                if success:
                    successful_tests += 1

            except Exception as e:
                self.log_conversation("SYSTEM", f"ERROR processing ticket {ticket.get('TicketID')}: {e}")

            # Brief pause between tickets
            await asyncio.sleep(5)

        # Test summary
        total_test_time = time.time() - self.test_start_time
        self.log_conversation("SYSTEM", "=== TEST SUMMARY ===")
        self.log_conversation("SYSTEM", f"Total Test Duration: {total_test_time:.1f} seconds")
        self.log_conversation("SYSTEM", f"Tickets Processed: {len(tickets)}")
        self.log_conversation("SYSTEM", f"Successful Tests: {successful_tests}")
        self.log_conversation("SYSTEM", f"Success Rate: {(successful_tests/len(tickets)*100):.1f}%")
        self.log_conversation("SYSTEM", f"Total Conversation Entries: {len(self.conversation_history)}")

        # Save conversation log
        self.save_conversation_log()

        return successful_tests == len(tickets)

    def save_conversation_log(self):
        """Save conversation history to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_log_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)

        self.log_conversation("SYSTEM", f"Conversation log saved to {filename}")

async def main():
    """Main test function"""
    print("=" * 80)
    print("LIVE ATERA WORKFLOW TEST - FULL CONVERSATION SIMULATION")
    print("=" * 80)
    print("Configuration:")
    print("- 30-minute timeout per ticket")
    print("- Real Atera API integration")
    print("- Full back-and-forth conversation")
    print("- Comprehensive logging")
    print("=" * 80)

    try:
        # Initialize test
        test = LiveAteraWorkflowTest()

        # Run comprehensive test
        success = await test.run_comprehensive_test()

        if success:
            print("\n" + "=" * 80)
            print("TEST COMPLETED SUCCESSFULLY!")
            print("All tickets processed with full conversation flows")
            print("Check the log files for detailed conversation history")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("TEST COMPLETED WITH ISSUES")
            print("Some tickets may not have processed correctly")
            print("Check the log files for details")
            print("=" * 80)

    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        logger.exception("Test failed with exception")

if __name__ == "__main__":
    asyncio.run(main())