# Roadmap & ToDos

## Resource Types
- FlexContainer
    - Support in &lt;AE>, &lt;Container>, &lt;flexContainers>
- Node
- ManagementObjects

## Features 
### Soon
- Add a setup.py for easier installation
- CSEBase, RemoteCSE, AE
	- nodelink attribute
- Announced resources

### Sometime
- Support offset, maxmimum number/size in retrievals
- Lazy retrieval of remote resources 
- Test with other oneM2M implementations (contributions needed)
- Support more &lt;subscription> attributes
	- eventNotificationCriteria, notificationStoragePriority, preSubscriptionNotify, pendingNotification, batchNotify, rateLimit, notificationEventCat,
	- Better handling of stale subscriptions. Currently the cse is not notified of stale subscriptions.