# Copyright (c) 2015, Adam Compton, Seeds of Epiphany LLC
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   Neither the name of Adam Compton or Seeds of Epiphany  nor the names of
#   its contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import json
import urllib2
 
class beefapi:

    def __init__(self, host="127.0.0.1", port="3000", token=""):
        self.CREDENTIALS = {"username":"beef", "password":"beef"}

        self.BEEF_HOST = host
        self.BEEF_PORT = port
        self.TOKEN = token
        self.RESTAPI_BASEURL = "http://%s:%s/api/" % (self.BEEF_HOST, self.BEEF_PORT)

        self.RESTAPI_HOOKS   = self.RESTAPI_BASEURL + "hooks"
        self.RESTAPI_LOGS    = self.RESTAPI_BASEURL + "logs"
        self.RESTAPI_MODULES = self.RESTAPI_BASEURL + "modules"
        self.RESTAPI_ADMIN   = self.RESTAPI_BASEURL + "admin"

    # ###########################################
    # Standard HTTP GET/POST Functions
    # ###########################################

    # send a GET request
    def http_get(self, url):
        req = urllib2.urlopen(url)
        data = json.loads(req.read())
        return data

    # send a POST request
    def http_post(self, url, post):
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(req, json.dumps(post))
        data = json.loads(response.read())
        return data

    # ###########################################
    # Help Functions Used to help With Code Reuse
    # ###########################################

    # helper function to get sessions
    def get_sessions(self, state, value):
        sessions = []
        data = self.http_get(self.RESTAPI_HOOKS + "?token=" + self.token)
        for item in data["hooked-browsers"][state].items():
            sessions.append(item[1][value])
        return sessions

    # ###########################################
    # Misc Functions
    # ###########################################

    # get api token 
    def get_token(self):
        data = self.http_post(self.RESTAPI_ADMIN + "/login", self.CREDENTIALS)
        self.token = data["token"]
        return self.token

    # ###########################################
    # Session Specific Functions
    # ###########################################

    # Get info about a aprticular session
    def get_session_info(self, session):
        data = self.http_get(self.RESTAPI_HOOKS + "?token=" + self.token)

        states = ["online", "offline"]
        for state in states:
            for item in data["hooked-browsers"][state].items():
                if item[1]["session"] == session:
                    return item[1]

    # Get browser info about a aprticular session
    def get_browser_info(self, session):
        return self.http_get(self.RESTAPI_HOOKS + "/%s?token=%s" % (session, self.token))

    # return all online sessions
    def get_online_sessions(self):
        return self.get_sessions("online", "session")

    # return all offline sessions
    def get_offline_sessions(self):
        return self.get_sessions("offline", "session")

    # get the associated Ip for a given session
    def session2ip(self, session):
        data = self.http_get(self.RESTAPI_HOOKS + "?token=" + self.token)
        states = ["online", "offline"]
        for state in states:
            for item in data["hooked-browsers"][state].items():
                if item[1]["session"] == str(session):
                    return item[1]["ip"]

    # ###########################################
    # Module Specific Functions
    # ###########################################

    # get list of available modules
    def get_modules(self):
        data = self.http_get(self.RESTAPI_MODULES + "?token=" + self.token)
        return data

    # get the module id associated with a given module name
    def module_name2id(self, name):
        modules = self.get_modules()
        for module in modules:
            if (modules[module]["name"] == name):
                return str(modules[module]["id"])

    # get information on a particular module
    def get_module_info(self, moduleid):
        data = self.http_get(self.RESTAPI_MODULES + "/" + moduleid + "?token=" + self.token)
        return data

    # execute a given module against a particular sessionid and then return the results
    def exec_module(self, sessionid, moduleid, post={}):
        data = self.http_post(self.RESTAPI_MODULES + "/" + sessionid + "/" + moduleid + "?token=" + self.token, post)
        return data["command_id"]

    # get the results of the command
    def get_module_results(self, sessionid, moduleid, commandid):
        return self.http_get(self.RESTAPI_MODULES + "/" + sessionid + "/" + moduleid + "/" + commandid + "?token=" + self.token)
 
if __name__ == "__main__":
    b = beefapi()
    b.get_token()
    sessions = b.get_online_sessions()
    print json.dumps(sessions, sort_keys=True, indent=4, separators=(',', ': '))
    for session in sessions:
        print json.dumps(b.get_session_info(session), sort_keys=True, indent=4, separators=(',', ': '))
        print json.dumps(b.get_browser_info(session), sort_keys=True, indent=4, separators=(',', ': '))
        print b.session2ip(session)
    print json.dumps(b.get_offline_sessions(), sort_keys=True, indent=4, separators=(',', ': '))
    print json.dumps(b.get_modules(), sort_keys=True, indent=4, separators=(',', ': '))
    moduleid = b.module_name2id("Get Internal IP WebRTC")
    print moduleid
    b.get_module_info(moduleid)
    sessionid = "ZW1zZhFcQNiKtlz4nYBC9h6DN3YLVknSW1hfyJgDFKfkdeZvCwUuEXWnQ29Y8whbrDyqyCsdwDHr677S"
    commandid = b.exec_module(sessionid, moduleid, post={})
    b.get_module_results(sessionid, moduleid, commandid)
