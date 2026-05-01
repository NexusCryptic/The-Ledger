#!/bin/bash
echo "🚀 AI Development Complete System"
echo "================================="
echo ""
echo "1. Launch ScreenerResearch 3-Window Environment"
echo "2. Launch Single ScreenerResearch Terminal"
echo "3. Launch Full AI Development Environment"
echo "4. Open AI Development Folder"
echo "5. View Chat Logs"
echo "6. View Reports"
echo "7. Debug Terminal Setup"
echo "8. Open Development Tools"
echo ""
read -p "Select option (1-8): " choice

case $choice in
    1) "/Users/MacInTosh/Desktop/AI_Development_Complete/Quick_Access/Launch_ScreenerResearch_3Window_Simple.command" ;;
    2) "/Users/MacInTosh/Desktop/AI_Development_Complete/Quick_Access/Launch_ScreenerResearch_Single.command" ;;
    3) "/Users/MacInTosh/Desktop/AI_Development_Complete/Quick_Access/Launch_Full_AI_Environment.command" ;;
    4) open "/Users/MacInTosh/Desktop/AI_Development_Complete" ;;
    5) open "/Users/MacInTosh/Desktop/AI_Development_Complete/Chat_Logs" ;;
    6) open "/Users/MacInTosh/Desktop/AI_Development_Complete/Reports" ;;
    7) "/Users/MacInTosh/Desktop/AI_Development_Complete/Quick_Access/Debug_Terminal_Setup.sh" ;;
    8) open "/Users/MacInTosh/Desktop/AI_Development_Complete/Development_Tools" ;;
    *) echo "Invalid option" ;;
esac
