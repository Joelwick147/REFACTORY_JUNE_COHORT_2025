Young4ChickS: A Brooder Management SystemProject OverviewYoung4ChickS is a web application designed to streamline the operations of a chick brooding and sales business. It offers a centralized platform for managing chick and feed stock, tracking sales, processing customer requests, and generating insightful reports for different user roles.
Key Features
###Brooder Managers: 
-Manage chick and feed inventory, approve/deny customer requests, and access detailed reports on stock valuation and chick performance.
###For Sales Representatives: 
-Submit chick requests on behalf of farmers, process sales transactions, and view dashboards with key sales performance indicators.Farmer Management: Register, update, and manage farmer information.

Public Request Tracker: A public page where farmers can track the status of their requests using a unique ID/NIN.
Technology StackBackend:
 Python 3.x, DjangoFrontend: HTML, CSS (Bootstrap 5), Database: Configurable, but uses SQLite by default for development.Styling: Bootstrap 5, custom CSS, and Font Awesome for icons.
 
Setup and Installation, Follow these steps to get the project running on your local machine.
 1.PrerequisitesEnsure you have Python 3.8+ and pip installed.
 2. Clone the Repositorygit clone https://github.com/Joelwick147/REFACTORY_JUNE_COHORT_2025.git
 
 3. Create a Virtual EnvironmentIt's highly recommended to use a virtual environment to manage dependencies:
 python -m venv venv
 Activate the virtual environment:Windows: venv\Scripts\activatemacOS/Linux: source venv/bin/activate
4. Install DependenciesInstall all required libraries using the provided requirements.txt file.pip install -r requirements.txt
   
6. Database MigrationsApply the initial database migrations to set up the database schema.python manage.py migrate

7. Create a SuperuserCreate an admin user to access the Django admin panel and manage the application.python manage.py createsuperuser
-Follow the prompts to set up your username, email, and password.
8. Create User RolesLog in to the Django admin panel (/admin) and create user accounts for each role (brooder_manager, sales_rep) to test the application's different views.
9. Run the Development ServerStart the Django development server to view the application in your browser.python manage.py runserver
-The application will be available at http://127.0.0.1:8000/.
