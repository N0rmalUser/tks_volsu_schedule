docker commit schedule schedule:latest
docker save -o schedule.tar schedule:latest
pscp -pw [password] schedule.tar admin1@10.0.0.103:/home/admin1/
ssh admin1@10.0.0.103 "docker stop schedule && \
 docker rm schedule && \
 docker load -i /home/admin1/schedule.tar && \
 docker run --name schedule \
 -d --restart=always \
 -v /home/admin1/data:/tks_schedule/data \
 -v /home/admin1/logs:/tks_schedule/logs \
 schedule"
rm schedule.tar