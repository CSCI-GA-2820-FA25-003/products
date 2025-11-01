$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#product_id").val(res.id);
        $("#product_name").val(res.name);
        $("#product_price").val(res.price);
        $("#product_description").val(res.description);
        $("#product_image_url").val(res.image_url);
        $("#product_category").val(res.category);
        if (res.availability == true) {
            $("#product_availability").val("true");
        } else {
            $("#product_availability").val("false");
        }
        if (res.discontinued == true) {
            $("#product_discontinued").val("true");
        } else {
            $("#product_discontinued").val("false");
        }
        if (res.favorited == true) {
            $("#product_favorited").val("true");
        } else {
            $("#product_favorited").val("false");
        }
        $("#product_created_date").val(res.created_date);
        $("#product_updated_date").val(res.updated_date);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_id").val("");
        $("#product_name").val("");
        $("#product_price").val("");
        $("#product_description").val("");
        $("#product_image_url").val("");
        $("#product_category").val("");
        $("#product_availability").val("");
        $("#product_discontinued").val("false");
        $("#product_favorited").val("false");
        $("#product_created_date").val("");
        $("#product_updated_date").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Product
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#product_name").val();
        let price = $("#product_price").val();
        let description = $("#product_description").val();
        let image_url = $("#product_image_url").val();
        let category = $("#product_category").val();
        let availability = $("#product_availability").val() == "true";
        let discontinued = $("#product_discontinued").val() == "true";
        let favorited = $("#product_favorited").val() == "true";


        let data = {
            "name": name,
            "price": price,
            "description": description,
            "image_url": image_url,
            "category": category,
            "availability": availability,
            "discontinued": discontinued,
            "favorited": favorited
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/products",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Product
    // ****************************************

    $("#update-btn").click(function () {
        let product_id = $("#product_id").val();
        let name = $("#product_name").val();
        let price = $("#product_price").val();
        let description = $("#product_description").val();
        let image_url = $("#product_image_url").val();
        let category = $("#product_category").val();
        let availability = $("#product_availability").val() == "true";
        let discontinued = $("#product_discontinued").val() == "true";
        let favorited = $("#product_favorited").val() == "true";

        let data = {
            "name": name,
            "price": price,
            "description": description,
            "image_url": image_url,
            "category": category,
            "availability": availability,
            "discontinued": discontinued,
            "favorited": favorited
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/products/${product_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Product
    // ****************************************

    $("#retrieve-btn").click(function () {

        let product_id = $("#product_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/products/${product_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Product
    // ****************************************

    $("#delete-btn").click(function () {

        let product_id = $("#product_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/products/${product_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Product has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#product_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Product
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#product_name").val();
        let category = $("#product_category").val();
        let availabilityVal = $("#product_availability").val();

        let queryString = "";

        if (availabilityVal !== "" && availabilityVal !== null) {
            let availability = availabilityVal === "true";
            queryString = "availability=" + availability;
        }

        if (name) {
            queryString = 'name=' + name
        }
        else if (category) {
            queryString = 'category=' + category
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/products?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = `
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th style="width: 5%;">ID</th>
                            <th style="width: 10%;">Name</th>
                            <th style="width: 10%;">Category</th>
                            <th style="width: 10%;">Price</th>
                            <th style="width: 8%;">Available</th>
                            <th style="width: 8%;">Discontinued</th>
                            <th style="width: 8%;">Favorited</th>
                            <th style="width: 15%;">Created Date</th>
                            <th style="width: 15%;">Updated Date</th>
                            <th style="width: 10%;">Image URL</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            let firstItem = "";

            for (let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `
                    <tr id="row_${i}">
                        <td>${item.id}</td>
                        <td>${item.name}</td>
                        <td>${item.category}</td>
                        <td>${item.price}</td>
                        <td>${item.availability}</td>
                        <td>${item.discontinued}</td>
                        <td>${item.favorited}</td>
                        <td>${item.created_date}</td>
                        <td>${item.updated_date}</td>
                        <td>${item.image_url ? `<a href="${item.image_url}" target="_blank">View</a>` : ''}</td>
                    </tr>
                `;

                if (i === 0) {
                    firstItem = item;
                }
            }

            table += `
                    </tbody>
                </table>
            `;

            $("#search_results").append(table);
            if (firstItem !== "") {
                update_form_data(firstItem);
            }
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
