from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

FEATURES={
 "small":{"student_profiles","terminal_results"},
 "mid":{"student_profiles","terminal_results","broadsheets","sms","fees"},
 "premium":{"student_profiles","terminal_results","broadsheets","sms","fees","cbt","payroll","expenses","online_fees"},
}
ROLE_PERMISSIONS={
 "proprietor":{"students.read","students.write","academics.read","academics.write","results.approve","results.lock","attendance","finance.read","finance.write","staff.manage","subscription.manage"},
 "headmaster":{"students.read","students.write","academics.read","academics.write","results.approve","results.lock","attendance","staff.assign"},
 "accountant":{"students.read","finance.read","finance.write"},
 "teacher":{"students.read","academics.read","academics.write","attendance"},
}

class SchoolContextMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        request.school=None; request.membership=None
        if request.user.is_authenticated and not request.user.is_superuser:
            membership=request.user.school_memberships.filter(is_active=True).select_related("school").first()
            if membership: request.membership=membership; request.school=membership.school
        return self.get_response(request)

def has_permission(request,permission):
    if request.user.is_superuser: return True
    membership=getattr(request,"membership",None)
    if not membership or not membership.school.subscription_is_valid: return False
    override=membership.custom_permissions.get(permission)
    return override if override is not None else permission in ROLE_PERMISSIONS.get(membership.role,set())

def permission_required(permission, feature=None):
    def decorator(view):
        @wraps(view)
        def wrapped(request,*args,**kwargs):
            if not request.user.is_authenticated: return redirect("login")
            if not has_permission(request,permission): raise PermissionDenied
            if feature and (not request.school or feature not in FEATURES[request.school.tier]): raise PermissionDenied("Your subscription tier does not include this feature.")
            return view(request,*args,**kwargs)
        return wrapped
    return decorator

def teacher_class_allowed(request,class_level,capability="can_enter_results"):
    if request.user.is_superuser or request.membership.role!="teacher": return True
    return request.membership.class_assignments.filter(class_level=class_level,**{capability:True}).exists()
