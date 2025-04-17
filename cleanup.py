import os
import shutil

def cleanup_project():
    # Files to delete
    files_to_delete = [
        'routes.py',
        '.flaskenv',
        'templates/auth.py',
        'templates/login.html',
        'templates/register.html'
    ]
    
    # Delete unnecessary files
    for file in files_to_delete:
        if os.path.exists(file):
            os.remove(file)
            print(f"Deleted: {file}")
    
    # Move pharmacy.db to instance if it exists
    if os.path.exists('pharmacy.db'):
        if not os.path.exists('instance'):
            os.makedirs('instance')
        shutil.move('pharmacy.db', 'instance/pharmacy.db')
        print("Moved pharmacy.db to instance directory")
    
    # Ensure auth templates are in the right place
    auth_templates = ['login.html', 'register.html']
    for template in auth_templates:
        src = os.path.join('templates', template)
        dst_dir = os.path.join('templates', 'auth')
        dst = os.path.join(dst_dir, template)
        if os.path.exists(src):
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            shutil.move(src, dst)
            print(f"Moved {template} to auth directory")

if __name__ == '__main__':
    cleanup_project()
