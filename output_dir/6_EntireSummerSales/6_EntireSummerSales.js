$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet1 = context.workbook.worksheets.getItem("Sheet1");
    const range = sheet1.getUsedRange();
    range.load("values");

    await context.sync();

    const promotionTotals: { [key: string]: number } = {};

    // Summarize total revenue for each promotion type
    for (let i = 1; i < range.values.length; i++) {
      const promotion = range.values[i][3]; // Column D: Promotion
      const revenue = range.values[i][6]; // Column G: Revenue

      if (promotion && revenue) {
        if (!promotionTotals[promotion]) {
          promotionTotals[promotion] = 0;
        }
        promotionTotals[promotion] += revenue;
      }
    }

    // Create a new sheet for the summary
    const summarySheet = context.workbook.worksheets.add("Promotion Summary");
    const headers = [["Promotion", "Total Revenue"]];
    const summaryData = Object.entries(promotionTotals).map(([promotion, total]) => [promotion, total]);

    // Set headers and data in the new sheet
    summarySheet.getRange("A1:B1").values = headers;
    summarySheet.getRange("A2:B" + (summaryData.length + 1)).values = summaryData;

    summarySheet.getUsedRange().format.autofitColumns();
    summarySheet.getUsedRange().format.autofitRows();

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