# dell-firmwareloader
Small python script which fetches all firmware from Dell reposiories. It can be easily add as cron-job.
And allows you to have DTK-compitable bundle folder.
Source code is based on comment from Dell support forum:
http://en.community.dell.com/support-forums/servers/f/177/p/19533117/20478213#20478213

Requirements:
- Python 2.7
- Python-requests
- Python-lxml
- Cabextract

One-line install of dependences for Debian flawors:
apt install cabextract python-requests python-lxml

Example for Dell R320:
./dell-fetcher.py --model 'R320/NX400' --storagelocation /srv/tftp/drm_files/repository/
