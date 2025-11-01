$(function () {

  // ---------------------------
  //  U T I L I T Y   F U N C S
  // ---------------------------

  function safeMessage(res, fallback = "Request failed") {
    try {
      if (res && res.responseJSON && res.responseJSON.message) return res.responseJSON.message;
      if (res && typeof res.responseText === "string" && res.responseText.trim()) return res.responseText;
    } catch (_) {}
    return fallback;
  }

  function update_form_data(res) {
    $("#product_id").val(res.id ?? "");
    $("#product_name").val(res.name ?? "");
    $("#product_price").val(res.price ?? "");
    $("#product_description").val(res.description ?? "");
    $("#product_image_url").val(res.image_url ?? "");
    $("#product_category").val(res.category ?? "");
    $("#product_availability").val((res.availability === true) ? "true" : "false");
    $("#product_discontinued").val((res.discontinued === true) ? "true" : "false");
    $("#product_favorited").val((res.favorited === true) ? "true" : "false");
    $("#product_created_date").val(res.created_date ?? "");
    $("#product_updated_date").val(res.updated_date ?? "");
  }

  function clear_form_data() {
    $("#product_id").val("");
    $("#product_name").val("");
    $("#product_price").val("");
    $("#product_description").val("");
    $("#product_image_url").val("");
    $("#product_category").val("");
    $("#product_availability").val(""); // empty/placeholder
    $("#product_discontinued").val("false");
    $("#product_favorited").val("false");
    $("#product_created_date").val("");
    $("#product_updated_date").val("");
  }

  function flash_message(message) {
    $("#flash_message").empty().append(message);
  }

  function payloadFromForm() {
    const priceRaw = $("#product_price").val();
    const price = priceRaw === "" ? null : Number(priceRaw);
    return {
      name: $("#product_name").val(),
      price: price,
      description: $("#product_description").val(),
      image_url: $("#product_image_url").val(),
      category: $("#product_category").val(),
      availability: $("#product_availability").val() === "true",
      discontinued: $("#product_discontinued").val() === "true",
      favorited: $("#product_favorited").val() === "true",
    };
  }

  // -------------
  //  C R E A T E
  // -------------
  $("#create-btn").on("click", function (e) {
    e.preventDefault();

    const data = payloadFromForm();

    // Minimal client-side check matching your help text
    if (!data.name || data.price === null || Number.isNaN(data.price)) {
      flash_message("Name and a numeric Price are required");
      return;
    }

    $("#flash_message").empty();

    $.ajax({
      type: "POST",
      url: "/products",
      contentType: "application/json",
      data: JSON.stringify(data),
    })
      .done(function (res) {
        update_form_data(res);
        flash_message("Success");
      })
      .fail(function (res) {
        flash_message(safeMessage(res, "Create failed"));
      });
  });

  // ------------
  //  U P D A T E
  // ------------
  $("#update-btn").on("click", function (e) {
    e.preventDefault();

    const product_id = $("#product_id").val().trim();
    if (!product_id) {
      flash_message("Please provide a Product ID to update");
      return;
    }

    const data = payloadFromForm();

    $("#flash_message").empty();

    $.ajax({
      type: "PUT",
      url: `/products/${encodeURIComponent(product_id)}`,
      contentType: "application/json",
      data: JSON.stringify(data),
    })
      .done(function (res) {
        update_form_data(res);
        flash_message("Success");
      })
      .fail(function (res) {
        flash_message(safeMessage(res, "Update failed"));
      });
  });

  // ---------------
  //  R E T R I E V E
  // ---------------
  $("#retrieve-btn").on("click", function (e) {
    e.preventDefault();

    const product_id = $("#product_id").val().trim();
    if (!product_id) {
      flash_message("Please enter an ID to retrieve");
      return;
    }

    $("#flash_message").empty();

    $.ajax({
      type: "GET",
      url: `/products/${encodeURIComponent(product_id)}`,
      contentType: "application/json",
    })
      .done(function (res) {
        update_form_data(res);
        flash_message("Success");
      })
      .fail(function (res) {
        clear_form_data();
        flash_message(safeMessage(res, "Retrieve failed"));
      });
  });

  // -----------
  //  D E L E T E
  // -----------
  $("#delete-btn").on("click", function (e) {
    e.preventDefault();

    const product_id = $("#product_id").val().trim();
    if (!product_id) {
      flash_message("Please enter an ID to delete");
      return;
    }

    $("#flash_message").empty();

    $.ajax({
      type: "DELETE",
      url: `/products/${encodeURIComponent(product_id)}`,
      contentType: "application/json",
    })
      .done(function () {
        clear_form_data();
        flash_message("Product has been Deleted!");
      })
      .fail(function (res) {
        flash_message(safeMessage(res, "Delete failed"));
      });
  });

  // ----------
  //  C L E A R
  // ----------
  $("#clear-btn").on("click", function (e) {
    e.preventDefault();
    $("#product_id").val("");
    $("#flash_message").empty();
    clear_form_data();
  });

  // -----------
  //  S E A R C H
  // -----------
  $("#search-btn").on("click", function (e) {
    e.preventDefault();

    const name = $("#product_name").val();
    const category = $("#product_category").val();
    const availabilityVal = $("#product_availability").val();

    let queryString = "";
    if (availabilityVal !== "" && availabilityVal !== null) {
      const availability = availabilityVal === "true";
      queryString = "availability=" + encodeURIComponent(availability);
    }
    if (name) {
      queryString = "name=" + encodeURIComponent(name);
    } else if (category) {
      queryString = "category=" + encodeURIComponent(category);
    }

    $("#flash_message").empty();

    $.ajax({
      type: "GET",
      url: `/products?${queryString}`,
      contentType: "application/json",
    })
      .done(function (res) {
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
          const item = res[i];
          table += `
            <tr id="row_${i}">
              <td>${item.id ?? ""}</td>
              <td>${item.name ?? ""}</td>
              <td>${item.category ?? ""}</td>
              <td>${item.price ?? ""}</td>
              <td>${item.availability}</td>
              <td>${item.discontinued}</td>
              <td>${item.favorited}</td>
              <td>${item.created_date ?? ""}</td>
              <td>${item.updated_date ?? ""}</td>
              <td>${item.image_url ? `<a href="${item.image_url}" target="_blank" rel="noopener noreferrer">View</a>` : ""}</td>
            </tr>
          `;
          if (i === 0) firstItem = item;
        }

        table += `</tbody></table>`;

        $("#search_results").append(table);
        if (firstItem !== "") update_form_data(firstItem);
        flash_message("Success");
      })
      .fail(function (res) {
        flash_message(safeMessage(res, "Search failed"));
      });
  });

});
