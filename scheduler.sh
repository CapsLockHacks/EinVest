while :
do
	echo "Bot Running! Press [CTRL+C] to stop.."
	curl http://10.1.24.70:5050/check_predictions/
	echo "Execution of Orders Executed"

	sleep 5
done
