import sys, SOAPpy

# Initialize connection to WebCtrl
class webctrlSOAP:
   def __init__(self):
      self.bacuser = ''
      self.password = ''
   
   def setValue(self, serverAddr, bacAddrPath, newVal):
      host = 'https://%s/_common/services/EvalService?wsdl' % (serverAddr)
      server = SOAPpy.SOAPProxy(host)
      server.SetValue(self.bacuser, self.password, bacAddrPath, '%s' % newVal)
      print 1
      return True
   
   def getValue(self, serverAddr, bacAddrPath):
      host = 'https://%s/_common/services/EvalService?wsdl' % (serverAddr)
      server = SOAPpy.SOAPProxy(host)
      value = server.GetValue(self.bacuser, self.password, bacAddrPath)
      print value
      return value

if len(sys.argv) > 1:
   obj = webctrlSOAP()

   if sys.argv[1] == "setValue":
      obj.setValue(sys.argv[2], sys.argv[3], sys.argv[4])

   elif sys.argv[1] == "getValue":
      obj.getValue(sys.argv[2], sys.argv[3])
