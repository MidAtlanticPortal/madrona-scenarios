madrona.onShow(function(){
    madrona.setupForm($('#wind-design-form'));
    
    var step = 1;
    var max_step = 3;

    $('.inputfield').each(function() {
        $(this).hide();
    });
    
    
    function validate(step) {
        if (step == 1) {/*
            parameter_selections = 0;
            var all_params = $('input.parameters');
            //NOTE:  This will also examine parameters in Step 2...might call those 'filters' to prevent this problem?
            //       This means the user could select a param in step 1, proceed to step 2, select param there, 
            //       return to step 1 and deselect all params there, and then proceed back to step 2 with no parameters selected
            //       or maybe call them parameters_step2...?
            $.each(all_params, function(index, param) {
                if (param.checked) {
                    parameter_selections += 1;
                }
            });
            if (parameter_selections == 0) {
                alert("Select at least 1 Criteria.");
                return false;
            } else {
                if ($('#id_input_parameter_wea').is(':checked')) {
                    wea_selections = 0;
                    $.each($('.wea_checkboxes'), function(index, checkbox) {
                        if (checkbox.checked) {
                            wea_selections += 1;
                        }
                    });
                    if (wea_selections == 0) {
                        alert("Select at least 1 Wind Energy Area or de-activate the Wind Energy Areas criteria.");
                        return false;
                    }
                }
            }*/
        } 
        return true;
    }; 

    function wizard(action) {
        if (step == 1 && action == 'next') {
            if (validate(step)) {
                step += 1;
            }
        } else if (step < max_step && action == 'next') {
            step += 1;
        } else if (step > 1 && action == 'prev') {
            step -= 1;
        }
        $('div.step').each(function(index) {
            $(this).hide();
        });
        $('div#step' + step).show();
        

        if (step == 1) {
            $('#button_prev').hide();
        //    $('#button_next').css('border-radius', '4px');
        } else {
            $('#button_prev').show();
        //    $('#button_next').css('border-top-right-radius', '4px');
        //    $('#button_next').css('border-bottom-right-radius', '4px');
        //    $('#button_next').css('border-top-left-radius', '0px');
        //    $('#button_next').css('border-bottom-left-radius', '0px');
        }

        if (step == max_step) {
            $('#button_next').hide();
            $('.submit_button').show();
        } else {
            $('#button_next').show();
            $('.submit_button').hide();
        }
    };
    
    function showhide_widget(element) {
        element.fadeToggle(100); //slideToggle
    }  
    
    function updateRemaininLeaseBlocks() {
        app.viewModel.scenarios.scenarioFormModel.updateLeaseblocksLeft();
        app.viewModel.scenarios.scenarioFormModel.updateRemainingBlocks();
    }
          
    // WIND SPEED UPDATED
    //Update Leaseblocks
    //slide ensures that leaseblocks are updated when the slider is adjusted
    //slidechange ensures that leaseblocks are updated when the text area is modified
    $('#slider-input_avg_wind_speed').bind( "slide slidechange", function(event, ui) {
        //var $left_side = $(event.target).find('.ui-slider-range');
        if (app.viewModel.scenarios.scenarioFormModel) {
            app.viewModel.scenarios.scenarioFormModel.change_wind_message(ui.value);
            app.viewModel.scenarios.scenarioFormModel.updateFilters({'key': 'wind', 'value': ui.value});
            updateRemaininLeaseBlocks();
        }
    });
          
    // DISTANCE TO SHORE UPDATED
    //Update Remaining Leaseblocks 
    $('#slider-input_distance_to_shore').bind( "slide slidechange", function(event, ui) {
        if (app.viewModel.scenarios.scenarioFormModel) { //this condition prevents error thrown at form creation time
            app.viewModel.scenarios.scenarioFormModel.updateFilters({'key': 'min_distance', 'value': ui.values[0]});
            app.viewModel.scenarios.scenarioFormModel.updateFilters({'key': 'max_distance', 'value': ui.values[1]});
            //Update Remaining Leaseblocks 
            updateRemaininLeaseBlocks();
        }
    });  
    
    
    // DEPTH RANGE UPDATED
    //Update Remaining Leaseblocks 
    $('#slider-input_depth').bind( "slide slidechange", function(event, ui) {
        if (app.viewModel.scenarios.scenarioFormModel) { //this condition prevents error thrown at form creation time
            app.viewModel.scenarios.scenarioFormModel.updateFilters({'key': 'min_depth', 'value': ui.values[0]});
            app.viewModel.scenarios.scenarioFormModel.updateFilters({'key': 'max_depth', 'value': ui.values[1]});
            //Update Remaining Leaseblocks 
            updateRemaininLeaseBlocks();
        }
    });
        
        
    // DISTANCE TO SUBSTATION UPDATED
    //Update Remaining Leaseblocks 
    $('#slider-input_distance_to_substation').bind( "slide slidechange", function(event, ui) {
        if (app.viewModel.scenarios.scenarioFormModel) { //this condition prevents error thrown at form creation time
            app.viewModel.scenarios.scenarioFormModel.updateFilters({'key': 'substation', 'value': ui.value});
            //Update Remaining Leaseblocks 
            updateRemaininLeaseBlocks();
        }
    }); 
    
     
    // DISTANCE TO AWC UPDATED
    //Update Remaining Leaseblocks 
    $('#slider-input_distance_to_awc').bind( "slide slidechange", function(event, ui) {
        if (app.viewModel.scenarios.scenarioFormModel) { //this condition prevents error thrown at form creation time
            app.viewModel.scenarios.scenarioFormModel.updateFilters({'key': 'awc', 'value': ui.value});
            //Update Remaining Leaseblocks 
            updateRemaininLeaseBlocks();
        }
    }); 

    
    // DISTANCE TO SHIPPING LANES UPDATED
    //Update Remaining Leaseblocks 
    $('#slider-input_distance_to_shipping').bind( "slide slidechange", function(event, ui) {
        if (app.viewModel.scenarios.scenarioFormModel) { //this condition prevents error thrown at form creation time
            app.viewModel.scenarios.scenarioFormModel.updateFilters({'key': 'tsz', 'value': ui.value});
            //Update Remaining Leaseblocks 
            updateRemaininLeaseBlocks();
        }
    }); 
       
    
    // TRAFFIC DENSITY UPDATED 
    /*
    $('#ship_traffic_density_widget').click( function(e) {
        if ( ! app.viewModel.scenarios.scenarioFormModel.shipTrafficDensityParameter() ) {
            app.viewModel.scenarios.scenarioFormModel.shipTrafficDensityParameter(true);
            $('#id_input_filter_ais_density').attr('checked', 'checked');
            app.viewModel.scenarios.scenarioFormModel.updateFilters({'key': 'ais', 'value': 1});
            //Update Remaining Leaseblocks 
            updateRemaininLeaseBlocks();
        } else {
            app.viewModel.scenarios.scenarioFormModel.shipTrafficDensityParameter(false);
            $('#id_input_filter_ais_density').removeAttr('checked');
            app.viewModel.scenarios.scenarioFormModel.removeFilter('ais');
            updateRemaininLeaseBlocks();
        }
    });
    */
            
    
    
    $('#button_prev').click( function() { wizard('prev'); });
    $('#button_next').click( function() { wizard('next'); });
    wizard();
    
    $('ul.errorlist').each( function() {
        step = 3;
        wizard();
    });
    
    //not sure this is used any more...
    /*
    $('img.info').each( function() {
        var id = $(this).attr('id');
        var text = "none";
        topMiddle = false;
        topLeft = false;
        topRight = false;
        switch(id) {
            //Step 1 Categories
            case 'info_wind_speed':
                topRight = true;
                text = $('#info_wind_speed_content').html();
                break;   
            case 'info_wind_speed_widget':
                topLeft = true;
                text = $('#info_wind_speed_widget_content').html();
                break;                        
            default:
                $(this).hide();
        }
        if (text != 'none') {                
            var my_configuration_object = {
                content: text, 
                show: { 
                    delay: 0,
                    when: { event: 'mouseover' } 
                },
                position: { corner: {} },
                hide: { when: {event: 'mouseleave'} },
                style: { 
                    name: 'blue' 
                }
            };
            if (topMiddle) {
                my_configuration_object.position.corner.target = 'topMiddle';
                my_configuration_object.position.corner.tooltip = 'bottomMiddle';
                my_configuration_object.style.width = 320;
            } else if (topLeft) {
                my_configuration_object.position.corner.target = 'topRight';
                my_configuration_object.position.corner.tooltip = 'bottomRight';
                my_configuration_object.style.width = 270;            
            } else if (topRight) {
                my_configuration_object.position.corner.target = 'topLeft';
                my_configuration_object.position.corner.tooltip = 'bottomLeft';
                my_configuration_object.style.width = 270;
            } else {
                my_configuration_object.position.corner.target = 'rightMiddle';
                my_configuration_object.position.corner.tooltip = 'leftMiddle';
                my_configuration_object.style.width = 270;
            }
            //$(this).qtip(my_configuration_object);
        }
    }); 
    */

     
    if ($("input[type='color']").length) {
        $.getScript("media/marco/js/mColorPicker.js");
    }   
    
    $('#id_name').keypress(function (e) {
        if (e.which === 13) {
            $('#scenario-form .submit_button').click();
            return false;
        } else {
            $('#invalid-name-message').hide();
        }
    });
    /*
    $('#scenario-form .submit_button').click( function() {
        var name = $('#id_name').val();
        if ($.trim(name) !== "") {  
            return true;
        }
        $('#invalid-name-message').show();
        return false;
    });
    */

    /* Tooltips */ 
    //overriding the template here to remove empty space for title
    $('.info-icon').popover({
        trigger: 'hover',
        template: '<div class="popover layer-popover"><div class="arrow"></div><div class="popover-inner layer-tooltip"><div class="popover-content"><p></p></div></div></div>'
    });
    $('.info-icon').click(function(e) {
        if ( $('.popover').is(':visible') ) {
            $('.popover').hide();
        }
    });
});
