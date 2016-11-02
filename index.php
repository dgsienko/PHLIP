

<form method='post' action=''>
	<input type='text' name='city'>
	<input type='submit' value='search city'>

</form>

<?php
$key = b25ff849273a05d3;
$url = 'http://api.wunderground.com/api/b25ff849273a05d3/conditions/q//MA/BOSTON.json';

$city = 'BOSTON';
if (isset($_POST['city'])) {
	$city = strtoupper($_POST['city']);
}


$json_string = file_get_contents("http://api.wunderground.com/api/b25ff849273a05d3/geolookup/conditions/q/MA/" . $city .".json");
  $parsed_json = json_decode($json_string);
  $location = $parsed_json->{'location'}->{'city'};
  $temp_f = $parsed_json->{'current_observation'}->{'temp_f'};

  echo "Current temperature in ${location} is: ${temp_f}\n";



?>