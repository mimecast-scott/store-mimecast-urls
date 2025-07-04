# Store Mimecast URLs locally

DICLAIMER: This is a proof of concept/example only and comes without warranty or support.

This service continuously monitors an IMAP mailbox for unread emails containing Mimecast-rewritten URLs (those with mimecastprotect.com). If detected the service decodes each of the rewritten URLS via the Mimecast API, and stores the mapping of encoded→decoded  (key→value) URLs in a lightweight PickleDB database. By running inside a Docker container under supervisord, it seamlessly handles both the mailbox polling and a FastAPI-powered lookup endpoint—so you can retrieve any previously decoded URL with a simple HTTP GET request.

While Mimecast’s rewritten links DO remain functional even after a customer leaves the platform. This tool ensures you always have a local archive of decoded URLs in the unlikely event that Mimecast’s service or API becomes unavailable, you’ll still be able to resolve links years down the track (assuming the URLs are still active). This approach gives organisations peace of mind, offloading the risk of link rot or service discontinuation without requiring any changes to existing email flows.


The container can be run with the following Docker command:

````
docker run -it -p 8000:8000 -p 9001:9001 -v ./data/:/opt/store-mimecast-urls/data/ -e CLIENT_ID="<-MIMECAST-CLIENT_ID-HERE->" -e CLIENT_SECRET="<-MIMECAST-CLIENT_SECRET-HERE->" -e IMAP_SERVER="<-IMAP_SERVER_IP->" -e IMAP_USERNAME="<-IMAP_USERNAME->" -e IMAP_PASSWORD="<-IMAP_PASSWORD->" smck83/store-mimecast-urls
````

supervisor webUI is available via
`http://localhost:9001`
admin/Admin

fastapi is available via
`http://localhost:8000/getAll`
or
`http://localhost:8000/get?key=<---mimecastprotect-url--->`
