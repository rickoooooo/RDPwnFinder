#!/bin/bash

# This script will scan an input list for open port 3389, then check for RDP security settings. It finds systems with native RDP encryption enabled and outputs their IPs.
# Example Usage: ./nmap-rdp-scanner.sh targetlist.txt > good_hosts.txt

targets=$1

nmap -iL $targets -p 3389 -n -Pn --script rdp-enum-encryption -oA ${targets}_nmap_results | grep -i "native rdp: success" -B8 | grep "Nmap scan report" |cut -d' ' -f5
