import re
#from pprint import pprint
import os
import json

class LogParser:
    log_line = ""
    parsed_data = {}
    """
    A class representing a single log with related parsing methods.

    Attributes:
        log_line (str): The log String.
        parsed_data (dict): Dictionaty containing each lined content parsed.
    """
    def __init__(self, log_line):
        self.log_line = log_line

    def parse(self):
        """
        Parses a log line and stores it in self.parsed_data.

        Parameters:
            none.
        """
        log_patterns = [
            r"^(?P<timestamp>[A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}) (?P<hostname>\S+) (?P<process>\S+) (?P<dc>\S+) (?P<errortype>\S+ \d+ \S+) (?P<processdetail>\S+ \S+ \S+) (?P<contextdetail>\S+ \S+ \S+ \S+) (?P<eventdesc>[\s\S]*\]) (?P<eventmessage>[\s\S]*)\"$",
            r"^(?P<timestamp>[A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}) (?P<hostname>\S+) (?P<process>\S+) (?P<dc>\S+) (?P<errortype>\S+ \d+ \S+) (?P<processdetail>\S+ \S+ \S+) (?P<eventdesc>\[[\s\S]*\]) (?P<eventmessage>[\s\S]*\")",
            r"^(?P<timestamp>[A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}) (?P<hostname>\S+) (?P<process>\S+) (?P<dc>\S+) (?P<errortype>\S+ \d+ \S+) (?P<processdetail>\S+ \S+ \S+) (?P<callid>\S+ \S+) \[Call Trace\] (?P<contextdetail>\S+ \S+ \S+ \S+)  (?P<eventdesc>[\s\S]*\]) (?P<eventmessage>[\s\S]*)"

        ]
        # to validate if a line matched any of the patterns
        matched_log = False
        for pat in log_patterns:
            pattern = pat
            match = re.match(pattern, self.log_line)
            if match:
                self.parsed_data = match.groupdict()
                matched_log = True
                break
        
        if not matched_log:
            print("Not Supported Log:\n" + self.log_line)
                
    
    def getParsedData(self):
        """
        Returns self.parsed_data.

        Returns:
            dict: parsed data dictionary.
        """
        if not self.parsed_data:
            self.parse()
        return self.parsed_data
    
class FileParser:
    log_group_for_summary = ["CONNECTEDAPPS ERROR","SCTP Association Term","sbPmNeedResend","MMES1PathFail","Unable to route message to host", "ManagerFailure",
                             "LicenseExceeded", "MMES1AssocFail", "MMES1AssocEstab", "MMES1PathEstab", "DUCON_NSA","SGSNHLRReset","TaskFailed",
                             "CLISessionStart", "CLISessionEnd", "SGSNGtpuPathFailureClear", "SGSNGtpuPathFailure","ManagerRestart","CseFailSwCoreNotifyExtended"
                             "detected path failure", "SGSNGtpcPathFailureClear", "SGSNGtpcPathFailure", "MME-APP encountered error","SessMgrRecoveryComplete",
                             "Restart Counter received in CREATE_PDP_CONTEXT_RESPONSE", "CPUWarnClear", "nsert-Subscriper-Data.EPS-Subscription-info validation failed",
                             "Authentication failed for user","Death notification of task sessmgr","Echo Response with restart counter",
                             "Session started for user", "have mini core, get evlogd status for logging crash file", "AAA client recovery process finished for AAA manager",
                             "Readdress successful for facility sessmgr instance", "CLI session started", "Sesssion stopped for user",
                             "LoginFailure", "Core file transfer to SPC complete", "Evlogd crashlog", "TaskRestart", "AAA client recovery process started for AAA manager",
                             "Readdress requested for facility sessmgr instance", "dropping S1AP packet", "Login attempt failure for user", "CLI command",
                             "Active CLI sessions count", "CLI session ended", "Core file transmitted to card", "Crash handler file transfer",
                             "rmmgr_collect_memstats_coproc_done", "Process sessmgr pid", "Restart Counter received", "detected restart for GGSN",
                             "dnode is NULL", "Error mapping event", "sbAsRcvShutdown", "update GGSN", "No GTPU Echo Response from GSN", "CseFailSwCoreNotifyExtended",
                             "rmmgr_collect_fdstats_coproc_done", "SGTPCMgr-3 detected path failure for","Session Setup Timer","Session start/disconnect Timer"]
    
    parsed_logs = []
    input_log_file_path = ""
    output_folder_path = "/binded/output/log_consolidation"
    """
    A class representing a single log with related parsing methods.

    Attributes:
        log_line (str): The log String.
        pased_data (dict): Dictionaty containing each lined content parsed.
    """

    def __init__(self, input_log_file_path, output_folder_path):
        self.input_log_file_path = input_log_file_path
        self.output_folder_path = output_folder_path

    def __init__(self, input_log_file_path):
        self.input_log_file_path = input_log_file_path
    
    def parseFile(self):
        print("Parsing file: "+self.input_log_file_path)
        try:
            with open(self.input_log_file_path, 'r') as file:
                for line in file:
                    #validating diffent line types in file for correct split
                    try:
                        if(len(line) > 40):
                            if(line.startswith(",\"")):
                                parser = LogParser(line.split(",\"")[2].split("\",")[0])
                            else:
                                parser = LogParser(line.split(",\"")[1].split("\",")[0])
                            parsed_log = parser.getParsedData()
                            if len(parsed_log) > 0:
                                self.parsed_logs.append(parsed_log)
                    except IndexError:
                        print("Line OOF: \n" + line)
        except FileNotFoundError:
            print("The file at {input_log_file_path} does not exist.")
        except IOError:
            print("An error occurred while trying to read the file at {input_log_file_path}.")
        print("File parsing complete.")
    
    def uniqueParsedLogs(self):
        """
        Returns list with unique messages found on the parsed log file.

        Returns:
            list: unique log messages.
        """
        unique_log = []
        for log_group in self.log_group_for_summary:
            unique_log.append(log_group)
        for log in self.parsed_logs:
            is_grouped_log = False
            for log_group in self.log_group_for_summary:
                if log_group in log["eventmessage"]:
                    is_grouped_log = True
                    break
            if not is_grouped_log and log["eventmessage"] not in unique_log:
                    unique_log.append(log["eventmessage"])
        return unique_log

    def log_message_count(self):
        """
        Counts the amount of times each log message shows on each log file.

        Returns:
            dict: containing mapping between each log message and number of times shows up in the file.
        """
        # Initialize log_statistics dictionary
        print("starting log_message_count")
        log_statistics = {}
        unique_log = self.uniqueParsedLogs()
        for log_message in unique_log:
            log_statistics.update({ log_message.replace("\"",'') : 0 })

        for log in self.parsed_logs:
            is_grouped_log = False
            for log_group in self.log_group_for_summary:
                if log_group in log["eventmessage"]:
                    log_statistics[log_group] += 1
                    is_grouped_log = True
                    break
            if not is_grouped_log:
                log_statistics[log["eventmessage"].replace("\"",'')] += 1
        print("Message count completed.")
        return log_statistics

    
    def logs_consolidation(log_dict1, log_dict2):
        """
        Adds log counts from both dictionaries

        Returns:
            dict: containing keys from both dictionaries, if keys are shared cuantities are added.
        """
        
        for dict2_keys in log_dict2.keys():
            try:
                log_dict1[dict2_keys] = log_dict1[dict2_keys] + log_dict2[dict2_keys]
            except KeyError:
                log_dict1.update({dict2_keys : log_dict2[dict2_keys]})
        return log_dict1
    
    def consolidation_json_dump(self):
        """
        Generates Summary dictionary containing number of log group repetition in file
         from log parsing dict and dumps the result in json format on output_file_path

        """
        log_statistics = self.log_message_count()
        print("output_file_path: "+os.path.join(self.output_folder_path, os.path.basename(self.input_log_file_path)) + "-summary.json")
        with open(os.path.join(self.output_folder_path, os.path.basename(self.input_log_file_path)) + "-summary.json", 'w') as json_file:
            json.dump(log_statistics, json_file, indent=4)



folder_path = "/binded/Syslog/"
total_dict = {}
for file in os.listdir(folder_path):
    file_parser = FileParser(os.path.join(folder_path, file))
    file_parser.parseFile()
    file_parser.consolidation_json_dump()

