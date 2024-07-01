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

![Fetching](https://cdn.discordapp.com/attachments/1244834155901222923/1253927608996069417/20240622_051755.jpg?ex=6677a296&is=66765116&hm=21ecaa02de8a7e48df146416da85848c8f36679b7ea1d4320381f73c171a40d9&)

![Platform 2 at Lanyon Place](https://cdn.discordapp.com/attachments/1244834155901222923/1253927609952243732/20240622_051814.jpg?ex=6677a297&is=66765117&hm=7d3c2bb7f61cf333cb1936c54c68b062a324eb1f22d48f65133fe7495b684555&)

![No Trains](https://cdn.discordapp.com/attachments/1244834155901222923/1253927610803556423/20240622_051937.jpg?ex=6677a297&is=66765117&hm=427a8b513abc602d435fd2efd50ed6d7969b3ce7c5ea36d169dbcd407f546b65&)

![Coleraine](https://cdn.discordapp.com/attachments/1244834155901222923/1253927776499798046/image.png?ex=6677a2be&is=6676513e&hm=99a00a85dadd52af32a8a30b511ca0be4dc0085bba992c42a0376bd6eecd04b5&)

