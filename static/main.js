import { $ } from "/static/jquery/src/jquery.js";

function say_hi(elt) {
    console.log("Welcome to", elt.text());
}

say_hi($("h1"));

/*
---------- Phase 2 ----------
*/
make_table_sortable($(".sortable"));
make_form_async($(".make_form_async"));
make_grade_hypothesized($(".make_grade_hypothesized"));

function make_table_sortable(table)
{
    const sortCell = table.find("thead th.sort-column");

    sortCell.on("click", function () {
        const index = $(this).index();

        const isAsc = $(this).hasClass("sort-asc");
        const isDesc = $(this).hasClass("sort-desc");
        const tbody = table.find("tbody");

        $(this).removeClass("sort-asc");
        $(this).removeClass("sort-desc");
        $(this).removeAttr("aria-sort");

        if(isAsc)
        {
            // if sorted in ascending, sort it on descending
            $(this).addClass("sort-desc");
            $(this).attr("aria-sort", "descending")
        }
        else if(isDesc){
            // if sorted on descending, sort on index
            $(this).attr("aria-sort", "ascending")
        }
        else{
            // if unsorted, sort in ascending
            $(this).addClass("sort-asc");
            $(this).attr("aria-sort", "ascending")
        }

        const rows = table.find("tbody tr").toArray();
        rows.sort((a, b) => {
            const td_a = $(a).find("td").get(index);
            const val_a = parseFloat($(td_a).data("value"));
            const td_b = $(b).find("td").get(index);
            const val_b = parseFloat($(td_b).data("value"));

            if ($(this).hasClass("sort-asc")) {
                return val_a - val_b;
            } 
            else if ($(this).hasClass("sort-desc")) {
                return val_b - val_a;
            }
            else {
                const val_a = $(a).data("index");
                const val_b = $(b).data("index");
                return val_a - val_b;
            }
        });

        $(rows).appendTo(table.find("tbody"));
    });
}

function make_form_async($form) {
    $form.on('submit', function (event) {
        event.preventDefault();
        const formData = new FormData(this);

        const $fileInput = $form.find('input[type="file"]');
        const $button = $form.find('input[type="submit"]');
        $fileInput.prop("disabled", true);
        $button.prop("disabled", true);

        $.ajax(
            {
                url: $form.attr("action"),
                data: formData,
                type: "POST",
                processData: false,
                contentType: false,
                mimeType: $form.attr("enctype"),
                success: function (response) {
                    $form.replaceWith("<p>Upload succeeded!</p>");
                },
                error: function (error) {
                    console.log("Error during submission:", error);
                    $fileInput.prop("disabled", false);
                    $button.prop("disabled", false);
                }
            }
        );
    });
}


function make_grade_hypothesized($table) {
    const $button = $('<button/>', {
                        text: 'Hypothesize',
                        class: 'hypothesize-button',
                    });

    $table.before($button);

    $button.on("click", function () {
        if ($table.hasClass("hypothesized")) {
            $table.removeClass("hypothesized");
            $button.text("Hypothesize");

            $table.find("tbody tr").each(function () {
                const $td = $(this).find("td:last");
                const ogText = $td.data("original-text");
                if (ogText) {
                    $td.text(ogText);
                }
            });
        } 
        else {
            $table.addClass("hypothesized");
            $button.text("Actual grades");

            $table.find("tbody tr").each(function () {
                const $td = $(this).find("td:last");
                const value = $td.text().trim();
                if (value === "Ungraded" || value === "Not Due") {
                    const $input = $("<input>").attr("type", "number").attr("min", 0).attr("max", 100);
                    $td.data("original-text", value);
                    $td.empty().append($input);
                }
            });
        }
        calculateGrade($table);
    });

    $table.on("keyup", "input", function () {
        calculateGrade($table);
    });

    // calculateGrade($table);
}


function calculateGrade($table) {
    let totalWeight = 0;
    let weightedScore = 0;

    $table.find("tbody tr").each(function () {
        const $td = $(this).find("td:last");
        // const weight = parseFloat($td.data("weight")) || 0;
        let weight = 0;
        let score = 0;

        if ($table.hasClass("hypothesized")) {
            const $input = $td.find("input");

            weight = parseFloat($td.data("weight"));

            if(!isNaN(parseFloat($td.data("value"))))
            {
                score += parseFloat($td.data("value")) / 100; // Counting the graded assignments
            }
            
            if ($input.length) {
                const inputVal = parseFloat($input.val());
                if (!isNaN(inputVal)) {
                    score = inputVal / 100; // Convert the % to decimal
                } 
                else {
                    return; // Skip
                }
            }   
        } 
        else{
            if($td.data("value") === "Missing" || parseFloat($td.data("value")))
            {
                weight = parseFloat($td.data("weight"));
            }

            if(!isNaN(parseFloat($td.data("value"))))
            {
                console.log($td.text());
                score += parseFloat($td.data("value")) / 100; // Using the student's actual grade
            }
        }

        totalWeight += weight;
        weightedScore += score * weight;
    });

    const finalGrade = totalWeight ? (weightedScore / totalWeight) * 100 : 0;
    $table.find("tfoot td:last").text(`${finalGrade.toFixed(2)}%`);
}