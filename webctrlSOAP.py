import sys, SOAPpy

# Initialize connection to WebCtrl
class webctrlSOAP:
   def __init__(self, username = 'DEFAULT', password= 'PASSWORD'):
      self.bacuser = username
      self.password = password
   
   def setValue(self, serverAddr, bacAddrPath, newVal):
      host = 'http://%s/_common/services/EvalService?wsdl' % (serverAddr)
      server = SOAPpy.SOAPProxy(host)
      server.SetValue(self.bacuser, self.password, bacAddrPath, '%s' % newVal)
      return True
   
   def getValue(self, serverAddr, bacAddrPath):
      host = 'http://%s/_common/services/EvalService?wsdl' % (serverAddr)
      server = SOAPpy.SOAPProxy(host)
      value = server.GetValue(self.bacuser, self.password, bacAddrPath)
      return value

if __name__ == "__main__":
   if len(sys.argv) > 1:
      obj = webctrlSOAP()
   
      if sys.argv[1] == "setValue":
         print obj.setValue(sys.argv[2], sys.argv[3], sys.argv[4])
   
      elif sys.argv[1] == "getValue":
         print obj.getValue(sys.argv[2], sys.argv[3])
