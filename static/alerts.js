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
				$('#suneffect').change(function() {
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
				$( "#suntest" ).click(function() {
					testcolor = $( "#suncolor" ).val();
					testlength = $( "#sunduration" ).val();
					testeffect = $( "#suneffect" ).val();
					$.post("http://localhost:5000/testlights", {color:testcolor, length:testlength, effect:testeffect});
				});
				     
		 }
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
					if($(this).val().length) {
						$('#tempcol').show();
						$('#tempdo').show();
						$('#tempalert').show();
						$('#tempsub').show();
						$('#temptest').show();   						
						$('#tempeffect').change(function(){
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
				$( "#temptest" ).click(function() {
					testcolor = $( "#tempcolor" ).val();
					testlength = $( "#tempduration" ).val();
					testeffect = $( "#tempeffect" ).val();
					$.post("http://localhost:5000/testlights", {color:testcolor, length:testlength, effect:testeffect});
				});
         
		 }
	});
	
	
});