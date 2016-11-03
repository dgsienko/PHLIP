

<form method='post' action=''>
	State:<input type='text' name='state' value=<?php echo $_POST['state']; ?>><br>
	City:<input type='text' name='city' value=<?php echo $_POST['city']; ?>><br>
	<input type='submit' value='Get Temperature'>

</form>

<?php

require_once 'config.php';

$key = b25ff849273a05d3;

$state = '';
$city = '';
if (isset($_POST['city']) && isset($_POST['state'])) {
	$city = strtoupper($_POST['city']);
	$state = strtoupper($_POST['state']);
}

$json_string = file_get_contents("http://api.wunderground.com/api/" . $key . "/geolookup/conditions/q/" . $state . "/" . $city . ".json");
$parsed_json = json_decode($json_string);

$location = $parsed_json->{'location'}->{'city'};
$temp_f = $parsed_json->{'current_observation'}->{'temp_f'};

echo "Current temperature in <strong>${location}</strong> is: ${temp_f}\n";



?>