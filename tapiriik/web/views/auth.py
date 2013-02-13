from django.http import HttpResponse
from django.shortcuts import render, redirect
from tapiriik.services import Service
from tapiriik.auth import User
import json

def auth_login(req, service):
    if "password" in req.POST:
        res = auth_do(req, service)
        if res:
            return redirect("dashboard")
    return render(req,"auth/login.html",{"serviceid":service,"service":Service.FromID(service)});

def auth_login_ajax(req, service):
    res = auth_do(req, service)
    return HttpResponse(json.dumps({"success": res}), mimetype='application/javascript')

def auth_do(req, service):
    svc = Service.FromID(service)
    uid, authData = svc.Authorize(req.POST["username"], req.POST["password"])
    if authData is not None:
        serviceRecord = Service.EnsureServiceRecordWithAuth(svc, uid, authData)
        # auth by this service connection
        existingUser = User.AuthByService(serviceRecord)
        # only log us in as this different user in the case that we don't already have an account
        if existingUser is not None and req.user is None:
            User.Login(existingUser, req)
        else:
            User.Ensure(req)
        # link service to user account, possible merge happens behind the scenes (but doesn't effect active user)
        User.ConnectService(req.user, serviceRecord)
        return True
    return False