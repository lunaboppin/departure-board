# Northern Ireland Railways departure board recreated in Python for a Raspberry Pi LCD Screen


Uses the Worldline Tiger API to fetch the data. Uses a NodeJS API running pupeteer to fetch the credentials and return back to the python script which calls the Tiger API.

## Features

- Randomly rotate between every station every 15 minutes
- Support for a button to swap to another station chosen at random
- Displays a message if there are no future trains at current station
- Platform data updates every minute
- Swaps displayed platform every minute






## Deployment

To deploy this project run

```bash
  cd api
  docker build -t browserpuppeteer-app
  docker run -d -p 3042:3042 browserpuppeteer-app
  cd ..
  python3 -m venv myenv
  source myenv/bin/activate
  pip install -r requirements.txt
  python __main__.py

  # OR RUN startup.sh to start the python script
```

Rename .env.example to .env and insert URL to API. For example,
http://127.0.0.1:3042/api/location


## Screenshots

![Fetching](https://raw.githubusercontent.com/boppinluna/departure-board/main/img/fetching.jpg)

![Platform 2 at Lanyon Place](https://raw.githubusercontent.com/boppinluna/departure-board/main/img/dublin.jpg)

![No Trains](https://raw.githubusercontent.com/boppinluna/departure-board/main/img/notrains.jpg)

![Coleraine](https://raw.githubusercontent.com/boppinluna/departure-board/main/img/station.png)

