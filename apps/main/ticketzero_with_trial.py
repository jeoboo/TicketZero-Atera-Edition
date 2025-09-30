"""
TicketZero AI - Atera Edition with Trial License Protection
This example shows how to integrate the trial system
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from trial_license import TrialGuard

# Original TicketZero workflow would be imported here
# from ticketzero_atera_workflow import main as run_ticketzero


def main():
    """Main entry point with trial protection"""

    # Initialize trial guard
    guard = TrialGuard(app_name="TicketZero AI - Atera Edition")

    # Check trial status
    if not guard.require_valid_trial():
        print("\n❌ Cannot start TicketZero - trial not valid")
        print(f"\n📧 To purchase a license, email: jgreenia@jandraisolutions.com")
        print(f"   Subject: TicketZero Atera Edition - License Purchase\n")
        sys.exit(1)

    # Show trial info if ending soon
    guard.show_trial_info_banner()

    print("="*70)
    print("  TicketZero AI - Atera Edition")
    print("  Automated Support Ticket Resolution")
    print("="*70)

    # Get trial status for display
    status = guard.get_status()
    if status.get('active'):
        days_left = status.get('days_remaining', 0)
        print(f"\n  📅 Trial Status: {days_left:.1f} days remaining")

    print("\n  Starting TicketZero workflow...")
    print("="*70 + "\n")

    # ===================================================================
    # YOUR TICKETZERO CODE RUNS HERE
    # ===================================================================

    # Example: Run the main TicketZero workflow
    # run_ticketzero()

    # For demonstration, just show that we got past the trial check
    print("✅ TicketZero is running with valid trial!\n")
    print("This is where your actual TicketZero workflow would execute:")
    print("  - Connect to Atera API")
    print("  - Fetch open tickets")
    print("  - Analyze with AI")
    print("  - Take automated actions")
    print("  - Update tickets\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  TicketZero interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
