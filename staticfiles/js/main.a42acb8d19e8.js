var collapse=true;
$(document).ready(function(){$('#menu-trigger').click(function(){
    if(collapse){$('#side-menu').animate({"width":"0px"});collapse=false;}else{$('#side-menu').animate({"width":"250px"});collapse=true} 
});//menutrigger click ends
});//document.ready ends
