#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Blog moderno y responsivo para hackers éticos con diseño cyberpunk/tema oscuro y acentos verde neón. Funcionalidades: feed de publicaciones con etiquetas (#web, #pentesting, #osint, #redteam, etc.), sistema de comentarios, búsqueda básica, navegación completa."

backend:
  - task: "Posts CRUD API"
    implemented: true
    working: "unknown"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "unknown"
        agent: "main"
        comment: "Implemented complete posts API with create, read, search, delete endpoints. Includes proper MongoDB integration with UUID, datetime handling, and tag filtering."

  - task: "Comments API"
    implemented: true
    working: "unknown"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "unknown"
        agent: "main"
        comment: "Implemented comments system with post association, CRUD operations and proper validation."

  - task: "Search and Tags API"
    implemented: true
    working: "unknown"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "unknown"
        agent: "main"
        comment: "Implemented search functionality with text search in title/content/tags, tag filtering, and popular tags aggregation endpoint."

frontend:
  - task: "Cyberpunk UI Design"
    implemented: true
    working: true
    file: "/app/frontend/src/App.css"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Successfully implemented cyberpunk design with dark theme, neon green accents (#00ff41), terminal-style prompts, glowing effects. Screenshot confirmed visual design is working perfectly."

  - task: "Feed de Publicaciones"
    implemented: true
    working: true
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Feed showing posts with hacking tags, responsive grid layout, clicking works. Sample posts created and displaying correctly. Screenshot confirmed functionality."

  - task: "Navigation System"
    implemented: true
    working: true
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Complete navigation with NeonSec branding, Inicio/Nueva Pregunta/Recursos links, cyberpunk styling. Screenshot confirmed working."

  - task: "Tag System"
    implemented: true
    working: "unknown"
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "unknown"
        agent: "main"
        comment: "Implemented tag filtering UI with popular hacking tags (web, pentesting, osint, redteam, etc.). Visual confirmed but backend interaction needs testing."

  - task: "Search Functionality"
    implemented: true
    working: "unknown"
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "unknown"
        agent: "main"
        comment: "Search input with terminal styling implemented. Frontend filtering works but backend API integration needs testing."

  - task: "Create Post Form"
    implemented: true
    working: "unknown"
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "unknown"
        agent: "main"
        comment: "Complete form for creating posts with title, content, tags, author fields. Cyberpunk styling applied. API integration needs testing."

  - task: "Comments System"
    implemented: true
    working: "unknown"
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "unknown"
        agent: "main"
        comment: "Post detail view with comments display and comment creation form. UI implemented but API integration needs testing."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 0
  run_ui: false

test_plan:
  current_focus:
    - "Posts CRUD API"
    - "Comments API"
    - "Search and Tags API"
    - "Create Post Form"
    - "Comments System"
    - "Tag System"
    - "Search Functionality"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "NeonSec hacker blog implemented with complete cyberpunk design and all core functionalities. Visual confirmation via screenshot shows perfect UI. Backend APIs implemented but need testing for Posts CRUD, Comments, Search/Tags. Frontend-backend integration for forms and data fetching needs verification. Sample data creation and API connectivity should be tested."