#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This python script includes many helpful defs that can be utilized in other arcpy scripts in order
to cut down on redundant coding.
Version 1.1
Publication Date: 02/11/2021
Author - Bradley Hall, GIS Support - Computer Services - ALDOT
Co-author Nam Dang - ALDOT Intern
"""

# import arcpy
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.request
import urllib.parse
import urllib.error
import contextlib
import time
import json
import os


def send_email(sender, receiver, subject, body, filename=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ", ".join(receiver)  # This must be a list, even if only one email address is being passed.
        msg['Subject'] = subject
        msg.attach(MIMEText(body))
        if filename is not None:
            with open(filename, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(filename)}",  # In case filename is a path
            )
            msg.attach(part)
        mailserver = smtplib.SMTP("cssendmail", 25)
        mailserver.ehlo()
        mailserver.starttls()

        mailserver.sendmail(sender, receiver, msg.as_string())
        mailserver.close()
    except Exception as genError:
        print("General Exception: {0}".format(genError))
        raise Exception(genError)


def write_log_file(fileandpath, texttowrite):
    try:
        logfile = open(fileandpath, "w")
        logfile.write(texttowrite)
        logfile.close()
    except Exception as genError:
        print("General Exception: {0}".format(genError))


def sendrequest(myrequest):
    try:
        # returns the response from an HTTP request in json format.
        with contextlib.closing(urllib.request.urlopen(myrequest)) as response:
            content = response.read()
            content_decoded = content.decode("utf-8")
            job_info = json.loads(content_decoded)
            return job_info
    except Exception as genError:
        raise Exception(genError)


def sendJSONRequest(myrequest):
    try:
        # Another way to get a response from a request.
        response = urllib.request.urlopen(myrequest)
        readResponse = response.read()
        jsonResponse = json.loads(readResponse)
        return jsonResponse
    except Exception as genError:
        raise Exception(genError)


def get_token(portalurl, uname, pword):
    try:
        # returns an authentication token for use in ArcGIS Online.
        params = {"username": uname,
                  "password": pword,
                  "referer": "https://aldot.maps.arcgis.com",
                  "f": "json"}

        token_url = "{}/generateToken".format(portalurl)
        data = urllib.parse.urlencode(params)
        data_encoded = data.encode("utf-8")
        request = urllib.request.Request(token_url, data=data_encoded)
        token_response = sendrequest(request)
        if "token" in token_response:
            print("Grabbing a token...")
            mytoken = token_response.get("token")
            return mytoken
        else:
            # Need to use HTTPS in this instance.
            if "error" in token_response:
                error_msg = token_response.get("error", {}).get("message")
                if "This request needs to be made over https." in error_msg:
                    token_url = token_url.replace("http://", "https://")
                    mytoken = get_token(token_url, uname, pword)
                    return mytoken
                else:
                    raise Exception("Portal Error: {} ".format(error_msg))
    except Exception as genError:
        print("General Exception: {0}".format(genError))


def get_tokenEnterprise(portalurl, uname, pword):
    try:
        # returns an authentication token for use in ArcGIS Online.
        params = {"username": uname,
                  "password": pword,
                  "referer": "https://csvgisas021.dot.state.al.us:6443",
                  "f": "json"}

        token_url = "{}/arcgis/admin/generateToken".format(portalurl)
        data = urllib.parse.urlencode(params)
        data_encoded = data.encode("utf-8")
        request = urllib.request.Request(token_url, data=data_encoded)
        token_response = sendrequest(request)
        if "token" in token_response:
            print("Grabbing a token...")
            mytoken = token_response.get("token")
            return mytoken
        else:
            # Need to use HTTPS in this instance.
            if "error" in token_response:
                error_msg = token_response.get("error", {}).get("message")
                if "This request needs to be made over https." in error_msg:
                    token_url = token_url.replace("http://", "https://")
                    mytoken = get_token(token_url, uname, pword)
                    return mytoken
                else:
                    raise Exception("Portal Error: {} ".format(error_msg))
    except Exception as genError:
        print("General Exception: {0}".format(genError))


def get_analysis_url(portalurl, token):
    try:
        # Return analysis URL from AGOL for running services
        print("Getting Analysis URL...")
        portals_self_url = "{}/portals/self?f=json&token={}".format(portalurl, token)
        request = urllib.request.Request(portals_self_url)
        portal_response = sendrequest(request)

        # Parse the dictionary from the json data response to get our Analysis URL...
        if "helperServices" in portal_response:
            helper_services = portal_response.get("helperServices")
            if "analysis" in helper_services:
                analysis_service = helper_services.get("analysis")
                if "url" in analysis_service:
                    analysis_url = analysis_service.get("url")
                    return analysis_url
        else:
            raise Exception("Unable to obtain Analysis URL.")
    except Exception as genError:
        print("General Exception: {0}".format(genError))


def analysis_job(analysis_url, task, token, params):
    try:
        # Submits an Analysis job then returns the job URL for monitoring the job's status in addition
        # to the JSON response data for teh submitted job.
        print("Submitting analysis job...")
        params["f"] = "json"
        params["token"] = token
        headers = {"Referer": "https://aldot.maps.arcgis.com"}
        task_url = "{}/{}".format(analysis_url, task)
        submit_url = "{}/submitJob?".format(task_url)
        data = urllib.parse.urlencode(params)
        data_encoded = data.encode("utf-8")
        request = urllib.request.Request(submit_url, data=data_encoded, headers=headers)
        analysis_response = sendrequest(request)
        if analysis_response:
            #  Print the response
            print(analysis_response)
            return task_url, analysis_response
        else:
            raise Exception("Unable to submit analysis job.")
    except Exception as genError:
        print("General Exception: {0}".format(genError))


def analysis_job_status(task_url, job_info, token):
    try:
        # Track the status of the submitted analysis job.
        if "jobId" in job_info:
            # Grab the ID of the analysis job to track status.
            job_id = job_info.get("jobId")
            job_url = "{}/jobs/{}?f=json&token={}".format(task_url, job_id, token)
            request = urllib.request.Request(job_url)
            job_response = sendrequest(request)

            # Query and report the analysis job status.
            if "jobStatus" in job_response:
                while not job_response.get("jobStatus") == "esriJobSucceeded":
                    time.sleep(5)
                    request = urllib.request.Request(job_url)
                    job_response = sendrequest(request)
                    print(job_response)

                    if job_response.get("jobStatus") == "esriJobFailed":
                        raise Exception("Job Failed!")
                    elif job_response.get("jobStatus") == "esriJobCancelled":
                        raise Exception("Job Cancelled!")
                    elif job_response.get("jobStatus") == "esriJobTimedOut":
                        raise Exception("Job Timed Out!")

                if "results" in job_response:
                    return job_response
            else:
                raise Exception("No job url!")
    except Exception as genError:
        print("General Exception: {0}".format(genError))


def analysis_job_results(task_url, job_info, token):
    try:
        # Get the paramUrl to get information regarding the Analysis job.
        if "jobId" in job_info:
            job_id = job_info.get("jobId")
            if "results" in job_info:
                results = job_info.get("results")
                result_values = {}
                for key in list(results.keys()):
                    param_value = results[key]
                    if "paramUrl" in param_value:
                        param_url = param_value.get("paramUrl")
                        result_url = "{}/jobs/{}/{}?token={}&f=json".format(task_url, job_id, param_url, token)
                        request = urllib.request.Request(result_url)
                        param_result = sendrequest(request)
                        job_value = param_result.get("value")
                        result_values[key] = job_value
                return result_values
            else:
                raise Exception("Unable to get analysis job results.")
        else:
            raise Exception("Unable to get analysis job results.")

    except Exception as genError:
        print("General Exception: {0}".format(genError))


def checkStatus(statusUrl, token):  # Check the status of our request/job.
    try:
        # statusURL = input("Enter the Status URL, please...")
        # token = input("Enter token:")
        tokenedStatusUrl = "{}?f=json&token={}".format(statusUrl, token)
        statusRequest = urllib.request.Request(tokenedStatusUrl)
        jsonResponse = sendrequest(statusRequest)

        while not jsonResponse.get("status") == "Completed":
            if jsonResponse.get("status") == "Failed":
                # Get out of our code if we receive a failed status.
                raise Exception("Process failed during replication!")
            else:
                time.sleep(30)
                # request = urllib.request.Request(tokenedStatusUrl)
                jsonResponse = sendrequest(statusRequest)
                print(jsonResponse['status'])

        if jsonResponse.get("status") == "Completed":
            resUrl = jsonResponse['resultUrl']
            tokenedResUrl = "{0}?token={1}".format(resUrl, token)
            return tokenedResUrl
    except Exception as genError:
        raise Exception(genError)

# I moved this def to another helper script specifically geared towards using arcpy functions.
# This removes the need for an ArcGIS Pro license being available for this script to be utilized.
# def create_temp_conn(connpath, sde, databasetype, instance, authtype):
#     try:
#         # Create SDE connection file in a temp location.
#         # This will be deleted when the script exits.
#         print("Creating temporary sde connection...")
#         print(connpath)
#         connectionPath = connpath
#         sdeName = sde
#         dbType = databasetype
#         dbInstance = instance
#         dbAuthType = authtype
#         geodbconnection = arcpy.CreateDatabaseConnection_management(connectionPath,
#                                                                     sdeName,
#                                                                     dbType,
#                                                                     dbInstance,
#                                                                     dbAuthType)
#         # Pass this geodb connection back to our caller...
#         return geodbconnection
#     except Exception as genError:
#         print("General Exception: {0}".format(genError))
#     except arcpy.ExecuteError as arcpyError:
#         errMsg = "Arcpy Exception: " + str(arcpy.GetMessages())
#         print(errMsg)
