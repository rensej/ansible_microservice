import re
#from pprint import pprint
import os
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import pandas
import traceback
import tempfile
import random
import time

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
            r"^(?P<timestamp>[A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}) (?P<hostname>\S+) (?P<process>\S+) (?P<dc>\S+) (?P<errortype>\S+ \d+ \S+) (?P<processdetail>\S+ \S+ \S+) (?P<contextdetail>\S+ \S+ \S+ \S+) (?P<eventdesc>[\s\S]*\]) (?P<eventmessage>[\s\S]*)$",
            r"^(?P<timestamp>[A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}) (?P<hostname>\S+) (?P<process>\S+) (?P<dc>\S+) (?P<errortype>\S+ \d+ \S+) (?P<processdetail>\S+ \S+ \S+) (?P<eventdesc>\[[\s\S]*\]) (?P<eventmessage>[\s\S]*)",
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
                del pat
                del match
                break
        
        if not matched_log:
            print("\nNot Supported Log:\n" + self.log_line)
                
    
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
                             "rmmgr_collect_fdstats_coproc_done", "SGTPCMgr-3 detected path failure for","Session Setup Timer","Session start/disconnect Timer", "S1AP Tx PDU, from",
                             "NAS Rx PDU, from", "changed from MME_EGTPC_STATE_RAB_REQ_PENDING to MME_EGTPC_STATE_ACTIVE", "from MME_EGTPC_STATE_ACTIVE to MME_EGTPC_STATE_RAB_REQ_PENDING",
                             "from MME_EGTPC_STATE_MOD_BRR_REQ_PENDING to MME_EGTPC_STATE_ACTIVE", "fsm event MME_EMM_EVENT_S1_RLS_REQ in state MME_EMM_STATE_REGISTERED_CONNECTED",
                             "fsm event MME_EMM_EVENT_IM_EXIT_TRIGGER in state MME_EMM_STATE_REGISTERED_CONNECTING","Completed MME Dual Conn NSA procedure  procedure with code 0",
                             "MME_EMM_FSM: Found procedure, msg type 10","Completed MME IM entry procedure  procedure with code 0",
                             "changed from MME_EGTPC_STATE_ACTIVE to MME_EGTPC_STATE_DWLINK_NOTF_PENDING"]
    
    parsed_logs = ""
    input_log_file_path = ""
    output_folder_path = "/home/output/log_consolidation"
    """
    A class representing a single log with related parsing methods.

    Attributes:
        log_line (str): The log String.
        pased_data (dict): Dictionaty containing each lined content parsed.
    """

    def __init__(self, input_log_file_path, output_folder_path):
        self.input_log_file_path = input_log_file_path
        self.output_folder_path = output_folder_path
        self.parsed_logs = "/home/temp-parsed-logs"+threading.current_thread().name + str(random.randint(100000, 999999))

    def __init__(self, input_log_file_path):
        self.input_log_file_path = input_log_file_path
        self.parsed_logs = "/home/temp-parsed-logs"+threading.current_thread().name + str(random.randint(100000, 999999))
    
    
    def parse_file(self):
        parsed_logs = []
        print("Parsing file: "+self.input_log_file_path)
        try:
            #log_raw = pandas.read_csv(self.input_log_file_path, usecols=["_raw"])
            log_raw_chunks = pandas.read_csv(self.input_log_file_path,chunksize=100000, usecols=["_raw"])
            for chunk in log_raw_chunks:
                print("Parsing chunk")
                for line in chunk["_raw"]:
                    #validating diffent line types in file for correct split
                    try:
                        if(len(line) > 10):
                            parser = LogParser(line)
                            parsed_log = parser.getParsedData()
                            if len(parsed_log) > 0:
                                parsed_logs.append(parsed_log)
                            del parsed_log
                            del parser
                    except IndexError:
                        print("Line OOF: \n" + line)
                del chunk
            del log_raw_chunks

            #dump parsed logs to file 
            df = pandas.DataFrame(parsed_logs)
            df.to_csv(self.parsed_logs, index=True)
            del df

        except FileNotFoundError:
            print("The file at {input_log_file_path} does not exist.")
        except IOError:
            print("An error occurred while trying to read the file at {input_log_file_path}.")
        except Exception as e:
            print(f"Error found on parse_file(): {e}")
        print("File parsing complete.")
    
    def uniqueParsedLogs(self):
        """
        Returns list with unique messages found on the parsed log file.

        Returns:
            list: unique log messages.
        """
        unique_log = []
        # for log_group in self.log_group_for_summary:
        #     unique_log.append(log_group)
        # for log in self.parsed_logs:
        #     is_grouped_log = False
        #     for log_group in self.log_group_for_summary:
        #         if log_group in log["eventmessage"]:
        #             is_grouped_log = True
        #             break
        #     if not is_grouped_log and log["eventmessage"] not in unique_log:
        #             unique_log.append(log["eventmessage"])
        #     del log
        
        for log_group in self.log_group_for_summary:
            unique_log.append(log_group)

        last_log= ""
        try:
            chunks = pandas.read_csv(self.parsed_logs, chunksize=100000, usecols=["eventmessage"])
            for chunk in chunks:
                print("Reading chunk for unique log detection in "+self.parsed_logs)
                for log in chunk["eventmessage"]:
                    is_grouped_log = False
                    if not isinstance(log, float):
                        for log_group in self.log_group_for_summary:
                            if log_group in log:
                                is_grouped_log = True
                                break
                        if not is_grouped_log and log not in unique_log:
                                unique_log.append(log)
                    del log
                del chunk
            del chunks
        except Exception as e:
            traceback.print_exc()
        return unique_log
    

    def log_message_count(self):
        """
        Counts the amount of times each log message shows on each log file.

        Returns:
            dict: containing mapping between each log message and number of times shows up in the file.
        """
        # Initialize log_statistics dictionary
        log_statistics = {}
        print("Log Statistics Dict Initialized")
        unique_log = self.uniqueParsedLogs()
        for log_message in unique_log:
            if len(log_message) > 1:
                log_statistics.update({ log_message : 0 })

        try:
            #loading from pandas for counting
            chunks = pandas.read_csv(self.parsed_logs, chunksize=100000, usecols=["eventmessage"])
            for chunk in chunks:
                print("Reading parsed log chunk")
                for log in chunk["eventmessage"]:
                    is_grouped_log = False
                    if not isinstance(log, float):
                        for log_group in self.log_group_for_summary:
                            # to avoid reading floats in file
                            if log_group in log:
                                log_statistics[log_group] += 1
                                is_grouped_log = True
                                break
                                
                        if not is_grouped_log:
                            log_statistics[log] += 1
                del chunk
            del chunks

            print("Message count completed.")
        except KeyError as key_error:
            print(f"KeyError: {key_error} - Check the log message format.")
        except Exception as e:
            print(f"An unexpected error occurred in log_message_count: {e}")
            traceback.print_exc()
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
    
    def consolidation_csv_dump(self):
        """
        Generates Summary dictionary containing number of log group repetition in file
         from log parsing dict and dumps the result in json format on output_file_path

        """
        
        try:
            log_statistics = self.log_message_count()
            print("Logs counted")
            df = pandas.DataFrame(FileParser.sort_consolidated_file(log_statistics), index=[0])
            print("Dumping log consolidation into: " +os.path.join(self.output_folder_path, os.path.basename(self.input_log_file_path)) + "-summary.csv")
            df.T.to_csv(os.path.join(self.output_folder_path, os.path.basename(self.input_log_file_path)) + "-summary.csv", index=True)
            del log_statistics
            del df
            os.remove(self.parsed_logs)
        except FileNotFoundError as fnf_error:
            print(f"Error: File not found - {fnf_error}")

        except PermissionError as perm_error:
            print(f"Error: Permission denied - {perm_error}")

        except Exception as e:
            # Catch any other unexpected exceptions
            traceback.print_exc()
            print(f"An unexpected error occurred: {e}")

        
        #with open(os.path.join(self.output_folder_path, os.path.basename(self.input_log_file_path)) + "-summary.json", 'w') as json_file:
            # Stores in json format a sorted vertion of the consolidated summary file
            #son.dump(FileParser.sort_consolidated_file(log_statistics), json_file, indent=4)
            # dumping as a csv file


    def multi_thread_processing(folder_path, workers_number):
        """
        Processes in multithreaded mode every log file

        Attributes:
            folder_path (str): output folder to store output files
            workers_number (int): number of max active threads working in the pool
        """
        def process_file(log_file):
            try:
                file_parser = FileParser(os.path.join(folder_path, log_file))
                file_parser.parse_file()
                file_parser.consolidation_csv_dump()
                file_parser.parsed_logs = []
                del file_parser
            except Exception as e:
                print(f"Error processing file {log_file}: {e}")
            
        
        # Multithreading with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=workers_number) as executor:
            file_list = os.listdir(folder_path)
            executor.map(process_file, file_list)
    
    def process_single_thread(folder_path):
        """
        Processes every log file in single thread mode

        Attributes:
            folder_path (str): output folder to store output files
        """
        file_list = os.listdir(folder_path)
        for log_file in file_list:
            try:
                file_parser = FileParser(os.path.join(folder_path, log_file))
                file_parser.parse_file()
                file_parser.consolidation_csv_dump()
                file_parser.parsed_logs = []
                del file_parser
            except Exception as e:
                print(f"Error processing file {log_file}: {e}")

    def sort_consolidated_file(unsorted_dict):
        return dict(sorted(unsorted_dict.items(), key=lambda item: item[1], reverse=True))


FileParser.multi_thread_processing("/home/Syslog/",4)
#FileParser.process_single_thread("/home/Syslog/")
