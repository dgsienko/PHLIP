/*
 * CS 411 Group 4
 * alerts.js
 * Shows and hides a bunch of divs in the HTML
 * Inelegant code, hastily prepared by Karan Varindani
 */

// Hides everything but the two radio buttons to start
$(document).ready(function() {
	$('#sunif').hide(); 
	$('#sundo').hide();
	$('#suncol').hide();
	$('#sunfor').hide();
	$('#sunalert').hide();
	$('#sunsub').hide();
	$('#suntest').hide();
	$('#tempif').hide(); 
	$('#tempdo').hide();
	$('#tempcol').hide(); 
	$('#tempfor').hide();
	$('#tempalert').hide(); 
	$('#tempsub').hide(); 
	$('#temptest').hide(); 
	
	$('input[type="radio"]').click(function() {
		// Functionality for Sunrise/Sunset radio 
		if($(this).attr('id') == 'sunid') {
				$('#tempif').hide(); 
				$('#tempdo').hide(); 
				$('#tempcol').hide();
				$('#tempfor').hide();
				$('#tempalert').hide(); 
				$('#tempsub').hide(); 
				$('#temptest').hide(); 
				
				$('#sunif').show(); 
				$('#sundo').show();
				$('#suncol').show();
				$('#sunalert').show();
				$('#sunsub').show();
				$('#suntest').show(); 
				$('#suneffect').change(function() { // Handler for the Effects drop-down
					if($(this).val() == 'flash') {
						$('#suncol').show();
						$('#sunalert').show();
						$('#sunfor').hide();
					}
					else if($(this).val() == 'on') {
						$('#suncol').show();
						$('#sunalert').hide();
						$('#sunfor').show();
					}
					else {
						$('#suncol').hide();
						$('#sunfor').show();
						$('#sunalert').hide();
					}
				});
				// Handler for the Test button (test lights)
				$( "#suntest" ).click(function() {
					testcolor = $( "#suncolor" ).val();
					testlength = $( "#sunduration" ).val();
					testeffect = $( "#suneffect" ).val();
					$.post("http://localhost:5000/testlights", {color:testcolor, length:testlength, effect:testeffect});
				});
				     
		 }
		 // Functionality for Temperature radio
		 if($(this).attr('id') == 'tempid') {
				$('#sunif').hide();
				$('#sundo').hide();
				$('#suncol').hide();
				$('#sunfor').hide();
				$('#sunalert').hide();
				$('#sunsub').hide();
				$('#suntest').hide();

				$('#tempif').show();   
				$('input[name="tempval"]').keyup(function(){
					if($(this).val().length) { // Checks to see if tempval has a value
						$('#tempcol').show();
						$('#tempdo').show();
						$('#tempalert').show();
						$('#tempsub').show();
						$('#temptest').show();   						
						$('#tempeffect').change(function(){ // Handler for the Effects drop-down
							if($(this).val() == 'flash') {
								$('#tempcol').show();
								$('#tempalert').show();
								$('#tempfor').hide();
							}
							else if($(this).val() == 'on') {
								$('#tempcol').show();
								$('#tempalert').hide();
								$('#tempfor').show();
							}
							else {
								$('#tempcol').hide();
								$('#tempfor').show();
								$('#tempalert').hide();
							}
						});
					}
					 else {
						$('#tempdo').hide();
						$('#tempcol').hide();
						$('#tempalert').hide();
						$('#tempsub').hide(); 
						$('#temptest').hide();
					}
				}); 
				// Handler for the Test button (test lights)
				$( "#temptest" ).click(function() {
					testcolor = $( "#tempcolor" ).val();
					testlength = $( "#tempduration" ).val();
					testeffect = $( "#tempeffect" ).val();
					$.post("http://localhost:5000/testlights", {color:testcolor, length:testlength, effect:testeffect});
				});
         
		 }
	});
	
	
});