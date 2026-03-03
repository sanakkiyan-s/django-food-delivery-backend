import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.user.models.user_role import Feature, UserRole, Permission
from apps.user.models.user import User
from apps.user.config import UserTypeChoices


def run_seed():
    print("🌱 Seeding Features and Roles...")

    # 1. Define your system features
    features = [
        "user_role_management",
        "admin_user_management",
        "menu_management",
        "order_management",
        "sales_reports",
        "customer_management"
    ]

    for identity in features:
        Feature.objects.get_or_create(identity=identity)
        print(f"  ✓ Feature created: {identity}")

    print("\n👑 Creating Admin Role...")
    
    # 2. Create the Role
    admin_role, created = UserRole.objects.get_or_create(
        identity="admin", 
        defaults={"description": "Administrator with full access to everything"}
    )
    
    # If the role already existed, create_default_permissions won't be called, 
    # but let's call it explicitly here just in case to ensure all permissions exist
    admin_role.create_default_permissions(permission_flag=False)

    # 3. Grant full access to everything for the Super Admin
    full_access = {
        "create": True, 
        "retrieve": True, 
        "update": True, 
        "delete": True
    }
    
    permissions_payload = {feature: full_access for feature in features}
    admin_role.update_all_permissions(permissions_payload)
    print("  ✓ Admin role created with full access to all features")

    print("\n👤 Setting up Admin User...")

    # 4. Create an Admin User (or use the existing one you made earlier)
    # Replace '9443341054' with the superuser phone number you created
    admin_number = "9443341054"
    
    user, created = User.objects.get_or_create(
        phone_number=admin_number,
        defaults={
            "name": "System Admin",
        }
    )
    
    if created:
        user.set_password("admin123@#")
        user.is_superuser = True
        user.is_staff = True
        
    user.user_type = UserTypeChoices.admin
    user.user_role = admin_role
    user.save()
    
    print(f"  ✓ User {admin_number} assigned as {user.user_type} with role {user.user_role.identity}")
    print("\n✅ Seeding Complete!")

if __name__ == "__main__":
    run_seed()
