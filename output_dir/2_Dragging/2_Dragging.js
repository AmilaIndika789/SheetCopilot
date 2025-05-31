$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    const range = sheet.getRange("B2:B122");

    // Fill down the formula from B2
    range.formulas = [[`=A2*9.81/0.75`]]; // Assuming the formula is based on m2 and g

    // Highlight cells based on the value
    const conditionalFormat = range.conditionalFormats.add(Excel.ConditionalFormatType.cellValue);
    conditionalFormat.cellValue.format.fill.color = "yellow"; // Default color for < 1
    conditionalFormat.cellValue.rule = {
      formula1: "1",
      operator: Excel.ConditionalCellValueOperator.lessThan
    };

    const conditionalFormatGreen = range.conditionalFormats.add(Excel.ConditionalFormatType.cellValue);
    conditionalFormatGreen.cellValue.format.fill.color = "green"; // Color for >= 1
    conditionalFormatGreen.cellValue.rule = {
      formula1: "1",
      operator: Excel.ConditionalCellValueOperator.greaterThanOrEqual
    };

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