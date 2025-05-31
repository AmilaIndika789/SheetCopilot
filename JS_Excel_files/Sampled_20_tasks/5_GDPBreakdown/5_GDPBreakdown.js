$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet1 = context.workbook.worksheets.getItem("Sheet1");
    const range = sheet1.getRange("P2:P3686");
    range.load("values");

    await context.sync();

    const results = range.values.map(row => [row[0] / 4]); // Convert years to quarters

    // Insert new column header
    const headerRange = sheet1.getRange("Q1");
    headerRange.values = [["2013 in Quarters"]];

    // Write results to the new column
    const resultRange = sheet1.getRange("Q2:Q3686");
    resultRange.values = results;

    await context.sync();
  });
}

/** Default helper for invoking an action and handling errors. */
async function tryCatch(callback) {
  try {
    await callback();
  } catch (error) {
    // Note: In a production add-in, you'd want to notify the user through your add-in's UI.
    console.error(error);
  }
}