$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem("Sheet1");
    const range = sheet.getUsedRange();
    
    // Load the values of the range
    range.load("values");
    await context.sync();

    // Calculate total sales and COGS
    let totalSales = 0;
    let totalCOGS = 0;

    for (let i = 1; i < range.values.length; i++) {
      totalSales += range.values[i][1]; // Sales column
      totalCOGS += range.values[i][2]; // COGS column
    }

    // Add a new row for totals
    const totalRow = range.getRowCount() + 1; // New row index
    sheet.getRange(`A${totalRow}:C${totalRow}`).values = [["Total", totalSales, totalCOGS]];

    // Calculate profit
    sheet.getRange(`D${totalRow}`).formulas = [["=B" + totalRow + "-C" + totalRow]]; // Profit formula

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