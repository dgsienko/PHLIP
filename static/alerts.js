$(document).ready(function() {
	$('#tempsub').hide(); 
	$('#sundiv').hide(); 
	$('#tempif').hide(); 
	$('#tempdo').hide(); 
	$('#tempfor').hide();
	$('#alertbox').hide(); 
	
	
	$('input[type="radio"]').click(function() {
		
		 if($(this).attr('id') == 'sunid') {
				$('#sundiv').show(); 
				$('#tempif').hide(); 
				$('#tempdo').hide(); 
				$('#tempfor').hide();
				$('#alertbox').hide();	
				$('#tempsub').hide();            
		 }
		 if($(this).attr('id') == 'tempid') {
				$('#tempif').show();   
				$('#sundiv').hide();
				$('input[name="tempval"]').keyup(function(){
					if($(this).val().length) {
						$('#tempdo').show();
						$('#alertbox').show();
						$('#tempsub').show();  						
						$('#effectdrop').change(function(){
							if($(this).val() == 'alert') {
								$('#alertbox').show();
								$('#tempfor').hide();
							}
							else {
								$('#tempfor').show();
								$('#alertbox').hide();
							}
						});
					}
					 else
						$('#tempdo').hide();
				});          
		 }
	});
});