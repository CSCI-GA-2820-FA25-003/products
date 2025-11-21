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

    // Show pagination info
    function show_pagination_info(page, limit) {
        $("#current_page_display").text(page);
        $("#current_limit_display").text(limit);
        $("#pagination_info").show();
    }

    // Hide pagination info
    function hide_pagination_info() {
        $("#pagination_info").hide();
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
            url: "/api/products",
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
                url: `/api/products/${product_id}`,
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
            url: `/api/products/${product_id}`,
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
            // Display appropriate error message based on status code
            if (res.status === 404) {
                flash_message("404 Not Found")
            } else if (res.responseJSON && res.responseJSON.message) {
                flash_message(res.responseJSON.message)
            } else {
                flash_message("Server error!")
            }
        });

    });

    // ****************************************
    // Favorite/unfavorite a Product
    // ****************************************
    $("#favorite-btn").click(function () {

        let product_id = $("#product_id").val();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/products/${product_id}/favorite`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            flash_message("Product has been marked as Favorite!");
        });

        ajax.fail(function(res){
            let msg = "Server error!";
            if (res.responseJSON && res.responseJSON.message) {
                msg = res.responseJSON.message;
            }
            flash_message(msg);
        });
    });


    $("#unfavorite-btn").click(function () {

        let product_id = $("#product_id").val();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/products/${product_id}/unfavorite`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            flash_message("Product has been un-favorited!");
        });

        ajax.fail(function(res){
            let msg = "Server error!";
            if (res.responseJSON && res.responseJSON.message) {
                msg = res.responseJSON.message;
            }
            flash_message(msg);
        });
    });

    // ****************************************
    // Discontinue a Product
    // ****************************************
    $("#discontinue-btn").click(function () {

        let product_id = $("#product_id").val();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: `/api/products/${product_id}/discontinue`,
            contentType: "application/json",
            data: JSON.stringify({"confirm": true}),
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Product has been Discontinued!");
        });

        ajax.fail(function(res){
            let msg = "Server error!";
            if (res.responseJSON && res.responseJSON.message) {
                msg = res.responseJSON.message;
            }
            flash_message(msg);
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
            url: `/api/products/${product_id}`,
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
        // Read search inputs
        const name = $("#product_name").val();
        const category = $("#product_category").val();
        const availabilityVal = $("#product_availability").val();

        // Determine whether this is a full list request
        const noFilters =
            (!name || name.trim() === "") &&
            (!category || category.trim() === "") &&
            (availabilityVal === "" || availabilityVal === null);

        $("#flash_message").empty();
        hide_pagination_info(); // Hide pagination info for search

        // fetch all products directly
        if (noFilters) {
            $.ajax({
                type: "GET",
                url: `/api/products`,
                contentType: "application/json",
                data: ""
            })
            .done(function (all) {
                renderResultsTable(all, { banner: "Showing all products." });
                flash_message("Empty search. Showing all products.");
            })
            .fail(function (err) {
                flash_message(err.responseJSON?.message || "Server error!");
            });
            return;
        }

        // try filtered search first
        let queryString = "";
        if (name && name.trim() !== "") {
            queryString = "name=" + encodeURIComponent(name.trim());
        } else if (category && category.trim() !== "") {
            queryString = "category=" + encodeURIComponent(category.trim());
        } else if (availabilityVal !== "" && availabilityVal !== null) {
            queryString = "availability=" + (availabilityVal === "true");
        }

        $.ajax({
            type: "GET",
            url: `/api/products?${queryString}`,
            contentType: "application/json",
            data: ""
        })
        .done(function (res) {
            if (Array.isArray(res) && res.length > 0) {
                // render only matches
                renderResultsTable(res);
                update_form_data(res[0]);
                flash_message("Success");
            } else {
                // flash not-found and fallback to full list
                flash_message("No matching products found. Showing all products.");
                $.ajax({
                    type: "GET",
                    url: `/api/products`,
                    contentType: "application/json",
                    data: ""
                })
                .done(function (all) {
                    renderResultsTable(all, { banner: "Showing all products." });
                })
                .fail(function (err) {
                    flash_message(err.responseJSON?.message || "Server error!");
                });
            }
        })
        .fail(function (err) {
            flash_message(err.responseJSON?.message || "Server error!");
        });
    });

    // ****************************************
    // Pagination Controls - NEW!
    // ****************************************

    $("#paginate-btn").click(function () {
        let page = parseInt($("#product_pagination_page").val()) || 1;
        let limit = parseInt($("#product_pagination_limit").val()) || 10;

        // Validate inputs
        if (page < 1) page = 1;
        if (limit < 1) limit = 10;
        if (limit > 100) limit = 100;

        // Update the input fields with validated values
        $("#product_pagination_page").val(page);
        $("#product_pagination_limit").val(limit);

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/products?page=${page}&limit=${limit}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            renderResultsTable(res);
            show_pagination_info(page, limit);
            if (res.length === 0) {
                flash_message(`No products found on page ${page}`);
            } else {
                flash_message(`Success - Showing page ${page} (${res.length} items)`);
            }
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON?.message || "Server error!");
        });
    });

    $("#reset-pagination-btn").click(function () {
        $("#product_pagination_page").val("1");
        $("#product_pagination_limit").val("10");
        hide_pagination_info();
        flash_message("Pagination reset");
    });

    // ****************************************
    // Render Results Table
    // ****************************************

    function renderResultsTable(list, options = {}) {
        $("#search_results").empty();

        const bannerHtml = options.banner
            ? `<div class="alert alert-info" style="padding:6px 10px; margin-bottom:8px;">${options.banner}</div>`
            : "";

        let table = `
            ${bannerHtml}
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

        if (!Array.isArray(list) || list.length === 0) {
            table += `<tr><td colspan="10" class="text-center">No products available.</td></tr>`;
        } else {
            list.forEach((item, i) => {
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
            });
        }

        table += `</tbody></table>`;
        $("#search_results").append(table);
    }

    // ****************************************
    // List All Products
    // ****************************************

    $("#list_all-btn").click(function () {

        $("#flash_message").empty();
        hide_pagination_info(); // Hide pagination info for list all

        let ajax = $.ajax({
            type: "GET",
            url: `/api/products`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
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
