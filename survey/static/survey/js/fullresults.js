function genericNumberFormatter(value, validFormatter) {
    switch (isNaN(value) || value) {
        case true:
            return "N/A";
        case Infinity:
            return "\u221e";
        default:
            return validFormatter(value);
    }
}

function percentageFormatter(value) {
    return genericNumberFormatter(value, v => parseFloat(v).toFixed(1) + "%");
}
function genderRatioFormatter(value) {
    return genericNumberFormatter(value, v => parseFloat(v).toFixed(2));
}
function scoreFormatter(value) {
    return genericNumberFormatter(value, v => parseFloat(v).toFixed(2));
}
function ageFormatter(value) {
    return genericNumberFormatter(value, v => parseFloat(v).toFixed(2));
}



function sortCompare(aRow, bRow, key, sortDesc, formatter, compareOptions, compareLocale) {
    const a = aRow[key];
    const b = bRow[key];

    if (key == "name") {
        // Sort names by the first official name (should be the Japanese name).
        const aName = a["official_name_list"][0];
        const bName = b["official_name_list"][0];
        return aName < bName ? -1 : aName > bName ? 1 : 0;
    }
    else if (typeof(a) == "number" && typeof(b) == "number") {
        // Treat NaN as the lowest number possible.
        if (isNaN(a)) return -1;
        if (isNaN(b)) return 1;
        return a < b ? -1 : a > b ? 1 : 0;
    }
    else {
        return null;
    }
}

function filterData(rows) {
    let result = [];
    for (let row of rows) {
        if (row["popularity"] > 0.0) {
            result.push(row);
        }
    }
    return result;
}

function rowClass(item, type) {
    if (item["popularity"] < 2.0) {
        return "text-danger";
    }
    else {
        return null;
    }
}

function getTableItems(animeData) {
    const tableItems = [];
    for (const anime_id in animeData) {
        const item = animeData[anime_id];
        item["name"] = animeInfo[anime_id];
        tableItems.push(item);
    }
    return tableItems;
}


const columnTypes = {
    name: {
        key: "name",
        label: "Anime",
    },
    popularity: {
        key: "popularity",
        label: "Popu-larity",
        formatter: percentageFormatter,
    },
    gender_popularity_ratio: {
        key: "gender_popularity_ratio",
        label: "Gender Ratio (♂:♀)",
        formatter: genderRatioFormatter,
    },
    gender_popularity_ratio_inv: {
        key: "gender_popularity_ratio_inv",
        label: "Gender Ratio (♀:♂)",
        formatter: genderRatioFormatter,
    },
    age: {
        key: "age",
        label: "Avg. Age",
        formatter: ageFormatter,
    },
    underwatched: {
        key: "underwatched",
        label: "Under-watched",
        formatter: percentageFormatter,
    },
    score: {
        key: "score",
        label: "Score",
        formatter: scoreFormatter,
    },
    gender_score_difference: {
        key: "gender_score_difference",
        label: "Score Diff. (♂-♀)",
        formatter: scoreFormatter,
    },
    gender_score_difference_inv: {
        key: "gender_score_difference_inv",
        label: "Score Diff. (♀-♂)",
        formatter: scoreFormatter,
    },
    surprise: {
        key: "surprise",
        label: "Sur-prise",
        formatter: percentageFormatter,
    },
    disappointment: {
        key: "disappointment",
        label: "Disa-ppoint-ment",
        formatter: percentageFormatter,
    }
};

for (let column_idx in columnTypes) {
    let column = columnTypes[column_idx];
    column["sortable"] = true;
    column["thStyle"] = column["key"] == "name" ? "width:300px" : "width:70px";
}

const animeSeriesColumns = [].concat([
    columnTypes["name"],
    columnTypes["popularity"],
    columnTypes["gender_popularity_ratio"],
    columnTypes["gender_popularity_ratio_inv"],
    columnTypes["age"]],
    surveyIsPreseason ? [
        columnTypes["underwatched"]
    ] : [], [
    columnTypes["score"],
    columnTypes["gender_score_difference"],
    columnTypes["gender_score_difference_inv"]],
    surveyIsPreseason ? [
        columnTypes["surprise"], columnTypes["disappointment"]
    ] : []
);
const specialAnimeColumns = [].concat([
    columnTypes["name"],
    columnTypes["popularity"],
    columnTypes["gender_popularity_ratio"],
    columnTypes["gender_popularity_ratio_inv"],
    columnTypes["age"]],
    surveyIsPreseason ? [
        columnTypes["score"], columnTypes["gender_score_difference"], columnTypes["gender_score_difference_inv"]
    ] : []
);

new Vue({
    el: "#results-table-series",
    delimiters: ["{$", "$}"],
    data: {
        fields: animeSeriesColumns,
        items: filterData(getTableItems(animeSeriesData)),
    },
});
new Vue({
    el: "#results-table-special",
    delimiters: ["{$", "$}"],
    data: {
        fields: specialAnimeColumns,
        items: filterData(getTableItems(specialAnimeData)),
    },
});