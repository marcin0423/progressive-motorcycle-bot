FROM public.ecr.aws/lambda/python:3.12 as build
RUN dnf install -y unzip && \
    curl -Lo "/tmp/chromedriver-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.78/linux64/chromedriver-linux64.zip" && \
    curl -Lo "/tmp/chrome-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.78/linux64/chrome-linux64.zip" && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/ && \
    unzip /tmp/chrome-linux64.zip -d /opt/
FROM public.ecr.aws/lambda/python:3.12
RUN dnf install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm
RUN pip install selenium==4.21.0
RUN pip install scrapy
RUN pip install webdriver_manager
COPY --from=build /opt/chrome-linux64 /opt/chrome
COPY --from=build /opt/chromedriver-linux64 /opt/chromedriver
RUN chmod +x /opt/chrome/chrome
RUN chmod +x /opt/chromedriver/chromedriver

COPY handler.py ./
ADD ProgressiveMotorcycleBot ProgressiveMotorcycleBot
copy scrapy.cfg ./

CMD [ "handler.main" ] 
