import onem2mlib.marshalling as M
import onem2mlib.internal as INT

class EventNotificationCriteria:
    """
    Indicates the conditions that shall be met to trigger a notification.
    """
    def __init__(self, **kwargs):
        self.createdBefore = kwargs.get('createdBefore')
        self.createdAfter = kwargs.get('createdAfter')
        self.modifiedSince = kwargs.get('modifiedSince')
        self.unmodifiedSince = kwargs.get('unmodifiedSince')
        self.stateTagSmaller = kwargs.get('stateTagSmaller')
        self.stateTagBigger = kwargs.get('stateTagBigger')
        self.expireBefore = kwargs.get('expireBefore')
        self.expireAfter = kwargs.get('expireAfter')
        self.sizeAbove = kwargs.get('sizeAbove')
        self.sizeBelow = kwargs.get('sizeBelow')
        self.notificationEventType = kwargs.get('notificationEventType', [])
        self.operationMonitor = kwargs.get('operationMonitor')
        self.attribute = kwargs.get('attribute')
        self.childResourceType = kwargs.get('childResourceType')
        self.missingData = kwargs.get('missingData')
        self.filterOperation = kwargs.get('filterOperation')

    def __str__(self):
        result = ''
        result += INT.strResource('createdBefore', 'crb', self.createdBefore)
        result += INT.strResource('createdAfter', 'cra', self.createdAfter)
        result += INT.strResource('modifiedSince', 'ms', self.modifiedSince)
        result += INT.strResource('unmodifiedSince', 'us', self.unmodifiedSince)
        result += INT.strResource('stateTagSmaller', 'sts', self.stateTagSmaller)
        result += INT.strResource('stateTagBigger', 'stb', self.stateTagBigger)
        result += INT.strResource('expireBefore', 'exb', self.expireBefore)
        result += INT.strResource('expireAfter', 'exa', self.expireAfter)
        result += INT.strResource('sizeAbove', 'sza', self.sizeAbove)
        result += INT.strResource('sizeBelow', 'szb', self.sizeBelow)
        result += INT.strResource('notificationEventType', 'net', self.notificationEventType)
        result += INT.strResource('operationMonitor', 'om', self.operationMonitor)
        result += INT.strResource('attribute', 'atr', self.attribute)
        result += INT.strResource('childResourceType', 'chty', self.childResourceType)
        result += INT.strResource('missingData', 'md', self.missingData)
        result += INT.strResource('filterOperation', 'fo', self.filterOperation)
        return result

    def _parseXML(self, root):
        M._EventNotificationCriteria_parseXML(self, root)

    def _createXML(self, isUpdate=False):
        return M._EventNotificationCriteria_createXML(self, isUpdate)

    def _parseJSON(self, jsn):
        M._EventNotificationCriteria_parseJSON(self, jsn)

    def _createJSON(self, isUpdate=False):
        return M._EventNotificationCriteria_createJSON(self, isUpdate)