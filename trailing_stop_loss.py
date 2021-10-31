def trailing_stop_loss(client,symbol,interval):

	#SparkBorsa Files 
	"""[summary]

		Args:
				account_number ([int])
				client ([obj])
				symbol ([str])
				interval ([str])

		Returns:
				obj 
	"""
	depth = 500  # depth of history , last X no of transactins
	tradehistory = client.get_my_trades(symbol = symbol, limit=depth) # 20 if want to sell based on only last buy order
	tradehistory = pd.DataFrame(tradehistory)

	if not tradehistory.empty:
		tradehistory = (tradehistory).tail(1)
		if tradehistory['isBuyer'].any() == True:
			del tradehistory['id']
			del tradehistory['commission']
			del tradehistory['commissionAsset']
			del tradehistory['isBestMatch']
			del tradehistory['orderListId']
			print(tradehistory)

			start_str = int(tradehistory['time'])
			pricepurchase = float(tradehistory['price'])


			Cdata = client.get_historical_klines(symbol, interval,start_str=start_str)

			df = pd.DataFrame(Cdata)
			if not df.empty:
				df[0] = pd.to_datetime(df[0], unit='ms')
				df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'IGNORE', 'Quote_volume', 'Trades_Count','BUY_VOL', 'BUY_VOL_VAL', 'x']
				df.set_index(pd.DatetimeIndex(df["date"]), inplace=True)

				df["open"] = pd.to_numeric(df["open"])
				df["high"] = pd.to_numeric(df["high"])
				df["low"] = pd.to_numeric(df["low"])
				df["close"] = pd.to_numeric(df["close"])
				df["volume"] = round(pd.to_numeric(df["volume"]))

				df["Quote_volume"] = round(pd.to_numeric(df["Quote_volume"]))
				df["Trades_Count"] = pd.to_numeric(df["Trades_Count"])
				

				del df['Trades_Count']
				del df['Quote_volume']
				del df['IGNORE']
				del df['BUY_VOL_VAL']
				del df['BUY_VOL']
				del df['x']
			#	print(df)



				maxhigh = (df.high).max()



				#lastprice getting from all_ticker['price']
				list_of_tickers = client.get_all_tickers()
				for tick_2 in list_of_tickers:					
					if tick_2["symbol"] == symbol:
						lastprice = float(tick_2["price"])
				


				trailing_stopLoss = float(20) # trailing stop loss pcg 
				trailing_stopLosspct = trailing_stopLoss/100

				sell_trailing_Sl = maxhigh - (maxhigh * trailing_stopLosspct) #PRICE OF STOP LOSS
				print('stop loss value : ', round(sell_trailing_Sl, 5))
				print('last price value : ', lastprice)

				if lastprice < sell_trailing_Sl:
					
					stoplossvalue = round(((sell_trailing_Sl - pricepurchase)/pricepurchase)*100 , 4)

					Asset = symbol[:-4].upper()
					qty = AccountFunction.AssetBalance(asset=Asset)
					
					qty = float(qty['free'])
					qty = qty- 0.01
				
					minQty = AccountFunction.pairQtyinfo( symbol, client)
					minPrice = AccountFunction.pairPriceinfo(symbol, client)

					AVG_price = AccountFunction.PairPrice(symbol)
					pluspricesell = AVG_price * 0.003
					lastpricesell = AVG_price - pluspricesell

					qtyFormatted = format_quantity(ticker = symbol, quantity = qty)
					priceFormatted = format_price(symbol, lastpricesell)

					
					try:

						side = 'SELL'
						executed = market_order(symbol,side, qtyFormatted,client)
						executed = 1 

						if executed == 1:
							info = f'Success hitted trailing stop loss on {symbol} with price {priceFormatted} /// trailingSL value {stoplossvalue}%'
							print(info)
							alert.alert(info)
							
							pass

					except Exception as e:
						infoerror = SP + "trailing stop loss failed (%s) " % e + 'on ' + symbol 							
						print(infoerror)
						#alert.alert(infoerror)
				
				else:
					print('trailing stop loss continue')

		else:
			pass
	else :
		pass

#sell market order execute
def execute_sell_market_order(symbol, quantity):
	order = client.order_market_sell(symbol=symbol, quantity=quantity)
	deleted_elements = ["orderListId", "timeInForce", "clientOrderId", "fills"]
	price = float(order["cummulativeQuoteQty"])/float(order["origQty"])
	order["price"] = format_price(symbol, price)
	for elem in deleted_elements:
		del order[elem]
	return order